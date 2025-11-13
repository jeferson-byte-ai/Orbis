"""Room management endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.db.session import get_db
from backend.db.models import User, Room, RoomParticipant, VoiceProfile
from backend.models.room import (
    CreateRoomRequest,
    RoomResponse,
    RoomDetailResponse,
    JoinRoomRequest,
    UpdateRoomConfigRequest,
    ParticipantResponse
)
from backend.api.deps import get_current_active_user
from backend.core.exceptions import NotFoundError, RoomFullError, AuthorizationError
from backend.config import settings

router = APIRouter(prefix="/api/rooms", tags=["Rooms"])


@router.post("", response_model=RoomResponse, status_code=201)
def create_room(
    request: CreateRoomRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new meeting room
    
    - **name**: Optional room name
    - **max_participants**: Maximum number of participants (2-100)
    - **pin**: Optional PIN for room protection
    - **input_language**: Language you speak ("auto" for auto-detect)
    - **output_language**: Language you want to hear
    - **voice_profile_id**: Voice to use in this room
    """
    # Get or create default voice if not specified
    voice_profile_id = request.voice_profile_id
    if not voice_profile_id:
        default_voice = db.query(VoiceProfile).filter(
            VoiceProfile.user_id == current_user.id,
            VoiceProfile.is_default == True
        ).first()
        if default_voice:
            voice_profile_id = default_voice.id
    
    # Auto-select languages from user preferences if "auto"
    input_lang = request.input_language
    output_lang = request.output_language
    
    if input_lang == "auto" and current_user.speaks_languages:
        # Use first language user speaks
        input_lang = current_user.speaks_languages[0]
    
    if output_lang == "auto" and current_user.understands_languages:
        # Use first language user understands
        output_lang = current_user.understands_languages[0]
    
    # Create room
    room = Room(
        name=request.name,
        creator_id=current_user.id,
        max_participants=request.max_participants,
        pin=request.pin,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.max_room_duration)
    )
    
    db.add(room)
    db.flush()  # Get room ID
    
    # Auto-join creator to room
    participant = RoomParticipant(
        room_id=room.id,
        user_id=current_user.id,
        voice_profile_id=voice_profile_id,
        input_language=input_lang,
        output_language=output_lang
    )
    
    db.add(participant)
    db.commit()
    db.refresh(room)
    
    return RoomResponse(
        id=room.id,
        name=room.name,
        creator_id=room.creator_id,
        max_participants=room.max_participants,
        is_active=room.is_active,
        participant_count=1,
        created_at=room.created_at
    )


@router.get("/{room_id}", response_model=RoomDetailResponse)
def get_room(
    room_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get room details with participants
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise NotFoundError("Room not found")
    
    # Get active participants
    participants = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.left_at == None
    ).all()
    
    # Build participant responses
    participant_responses = []
    for p in participants:
        user = db.query(User).filter(User.id == p.user_id).first()
        voice = db.query(VoiceProfile).filter(VoiceProfile.id == p.voice_profile_id).first() if p.voice_profile_id else None
        
        participant_responses.append(ParticipantResponse(
            id=p.id,
            user_id=p.user_id,
            username=user.username if user else "Unknown",
            input_language=p.input_language,
            output_language=p.output_language,
            voice_profile_name=voice.name if voice else None,
            joined_at=p.joined_at
        ))
    
    return RoomDetailResponse(
        id=room.id,
        name=room.name,
        creator_id=room.creator_id,
        max_participants=room.max_participants,
        is_active=room.is_active,
        participant_count=len(participants),
        created_at=room.created_at,
        participants=participant_responses
    )


@router.post("/{room_id}/join", response_model=ParticipantResponse)
def join_room(
    room_id: UUID,
    request: JoinRoomRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Join a meeting room
    
    - **pin**: Room PIN (if required)
    - **input_language**: Language you speak
    - **output_language**: Language you want to hear
    - **voice_profile_id**: Voice to use
    """
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise NotFoundError("Room not found")
    
    if not room.is_active:
        raise HTTPException(status_code=410, detail="Room is no longer active")
    
    # Check PIN
    if room.pin and room.pin != request.pin:
        raise AuthorizationError("Invalid PIN")
    
    # Check if already in room
    existing = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.id,
        RoomParticipant.left_at == None
    ).first()
    
    if existing:
        # Already in room, just return
        user = db.query(User).filter(User.id == existing.user_id).first()
        voice = db.query(VoiceProfile).filter(VoiceProfile.id == existing.voice_profile_id).first() if existing.voice_profile_id else None
        
        return ParticipantResponse(
            id=existing.id,
            user_id=existing.user_id,
            username=user.username,
            input_language=existing.input_language,
            output_language=existing.output_language,
            voice_profile_name=voice.name if voice else None,
            joined_at=existing.joined_at
        )
    
    # Check room capacity
    active_count = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.left_at == None
    ).count()
    
    if active_count >= room.max_participants:
        raise RoomFullError(f"Room is full (max {room.max_participants} participants)")
    
    # Get voice profile
    voice_profile_id = request.voice_profile_id
    if not voice_profile_id:
        default_voice = db.query(VoiceProfile).filter(
            VoiceProfile.user_id == current_user.id,
            VoiceProfile.is_default == True
        ).first()
        if default_voice:
            voice_profile_id = default_voice.id
    
    # Auto-select languages from user preferences if "auto"
    input_lang = request.input_language
    output_lang = request.output_language
    
    if input_lang == "auto" and current_user.speaks_languages:
        # Use first language user speaks
        input_lang = current_user.speaks_languages[0]
    
    if output_lang == "auto" and current_user.understands_languages:
        # Use first language user understands
        output_lang = current_user.understands_languages[0]
    
    # Join room
    participant = RoomParticipant(
        room_id=room_id,
        user_id=current_user.id,
        voice_profile_id=voice_profile_id,
        input_language=input_lang,
        output_language=output_lang
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    voice = db.query(VoiceProfile).filter(VoiceProfile.id == voice_profile_id).first() if voice_profile_id else None
    
    return ParticipantResponse(
        id=participant.id,
        user_id=participant.user_id,
        username=current_user.username,
        input_language=participant.input_language,
        output_language=participant.output_language,
        voice_profile_name=voice.name if voice else None,
        joined_at=participant.joined_at
    )


@router.post("/{room_id}/leave")
def leave_room(
    room_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Leave a meeting room
    """
    participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.id,
        RoomParticipant.left_at == None
    ).first()
    
    if not participant:
        raise NotFoundError("Not in this room")
    
    # Mark as left
    participant.left_at = datetime.utcnow()
    db.commit()
    
    # Check if room is now empty
    remaining = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.left_at == None
    ).count()
    
    if remaining == 0:
        # Deactivate room if empty
        room = db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.is_active = False
            db.commit()
    
    return {"success": True, "message": "Left room"}


@router.patch("/{room_id}/config", response_model=ParticipantResponse)
def update_room_config(
    room_id: UUID,
    request: UpdateRoomConfigRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update your configuration in a room (language, voice) during meeting
    """
    participant = db.query(RoomParticipant).filter(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == current_user.id,
        RoomParticipant.left_at == None
    ).first()
    
    if not participant:
        raise NotFoundError("Not in this room")
    
    # Update config
    if request.input_language is not None:
        participant.input_language = request.input_language
    if request.output_language is not None:
        participant.output_language = request.output_language
    if request.voice_profile_id is not None:
        # Verify voice belongs to user
        voice = db.query(VoiceProfile).filter(
            VoiceProfile.id == request.voice_profile_id,
            VoiceProfile.user_id == current_user.id
        ).first()
        if not voice:
            raise NotFoundError("Voice profile not found")
        participant.voice_profile_id = request.voice_profile_id
    
    db.commit()
    db.refresh(participant)
    
    voice = db.query(VoiceProfile).filter(VoiceProfile.id == participant.voice_profile_id).first() if participant.voice_profile_id else None
    
    return ParticipantResponse(
        id=participant.id,
        user_id=participant.user_id,
        username=current_user.username,
        input_language=participant.input_language,
        output_language=participant.output_language,
        voice_profile_name=voice.name if voice else None,
        joined_at=participant.joined_at
    )


@router.delete("/{room_id}")
def delete_room(
    room_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a room (only creator can delete)
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise NotFoundError("Room not found")
    
    if room.creator_id != current_user.id:
        raise AuthorizationError("Only room creator can delete the room")
    
    db.delete(room)
    db.commit()
    
    return {"success": True, "message": "Room deleted"}


@router.get("", response_model=List[RoomResponse])
def list_my_rooms(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List rooms created by current user
    """
    rooms = db.query(Room).filter(
        Room.creator_id == current_user.id,
        Room.is_active == True
    ).all()
    
    responses = []
    for room in rooms:
        count = db.query(RoomParticipant).filter(
            RoomParticipant.room_id == room.id,
            RoomParticipant.left_at == None
        ).count()
        
        responses.append(RoomResponse(
            id=room.id,
            name=room.name,
            creator_id=room.creator_id,
            max_participants=room.max_participants,
            is_active=room.is_active,
            participant_count=count,
            created_at=room.created_at
        ))
    
    return responses
