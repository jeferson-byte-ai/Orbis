/**
 * i18n Translations for Orbis
 * Supports multiple languages for the user interface
 */

import { settingsTranslations } from './settingsTranslations';
import { homeTranslations } from './homeTranslations';

export const translations = {
  en: {
    ...settingsTranslations.en,
    ...homeTranslations.en,
    // Common
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Close',
    loading: 'Loading...',
    success: 'Success!',
    error: 'Error',
    
    // Navigation
    home: 'Home',
    settings: 'Settings',
    profile: 'Profile',
    logout: 'Sign Out',
    
    // Settings Page
    settings_title: 'Settings',
    profile_tab: 'Profile',
    account_tab: 'Account',
    security_tab: 'Security',
    preferences_tab: 'Preferences',
    notifications_tab: 'Notifications',
    audio_tab: 'Audio & Video',
    danger_tab: 'Danger Zone',
    
    // Preferences
    preferences_title: 'Preferences',
    theme_label: 'Theme',
    theme_light: 'Light',
    theme_dark: 'Dark',
    theme_auto: 'Auto (System)',
    language_label: 'Language',
    auto_detect_input: 'Auto-detect input language',
    auto_detect_output: 'Auto-detect output language',
    save_preferences: 'Save Preferences',
    preferences_saved: 'Preferences saved successfully!',
    
    // Profile
    profile_title: 'Profile Information',
    full_name: 'Full Name',
    bio: 'Bio',
    company: 'Company',
    job_title: 'Job Title',
    update_profile: 'Update Profile',
    profile_updated: 'Profile updated successfully!',
    
    // Security
    security_title: 'Security',
    change_password: 'Change Password',
    current_password: 'Current Password',
    new_password: 'New Password',
    confirm_password: 'Confirm New Password',
    password_changed: 'Password changed successfully!',
    two_factor_auth: 'Two-Factor Authentication',
    enable_2fa: 'Enable 2FA',
    
    // Danger Zone
    danger_title: 'Danger Zone',
    delete_account: 'Delete Account',
    delete_account_warning: 'Once you delete your account, there is no going back. Please be certain.',
    delete_forever: 'Delete Forever',
    
    // Notifications
    notifications_title: 'Notification Settings',
    email_notifications: 'Email Notifications',
    push_notifications: 'Push Notifications',
    meeting_reminders: 'Meeting Reminders',
    new_features: 'New Features',
    
    // Audio
    audio_title: 'Audio & Video Settings',
    microphone_volume: 'Microphone Volume',
    speaker_volume: 'Speaker Volume',
    echo_cancellation: 'Echo Cancellation',
    noise_suppression: 'Noise Suppression',
    reduce_echo: 'Reduce echo in calls',
    filter_noise: 'Filter background noise',
    save_audio_settings: 'Save Audio Settings',
    
    // Account
    account_title: 'Account Information',
    email: 'Email',
    username: 'Username',
    email_cannot_change: 'Email cannot be changed. Contact support if needed.',
    username_cannot_change: 'Username cannot be changed.',
    account_status: 'Account Status',
    email_verified: 'Email Verified',
    email_verified_desc: 'Your email is verified',
    free_plan: 'Free Plan',
    free_plan_desc: 'Basic features included',
    
    // Profile
    profile_settings: 'Profile Settings',
    your_full_name: 'Your full name',
    tell_about_yourself: 'Tell us about yourself...',
    your_company: 'Your company',
    your_role: 'Your role',
    save_changes: 'Save Changes',
    saving: 'Saving...',
    
    // Security details
    security_settings: 'Security Settings',
    enter_current_password: 'Enter current password',
    enter_new_password: 'Enter new password',
    confirm_new_pass: 'Confirm new password',
    add_extra_security: 'Add an extra layer of security to your account',
    
    // Notifications details
    receive_email_notif: 'Receive notifications via email',
    get_browser_notif: 'Get notified in your browser',
    remind_before_meetings: 'Remind me before meetings start',
    learn_new_features: 'Learn about new features and updates',
    save_notification_settings: 'Save Notification Settings',
    notification_settings_saved: 'Notification settings saved!',
    audio_settings_saved: 'Audio settings saved!',
    
    // Danger Zone details
    no_going_back: 'Once you delete your account, there is no going back. Please be certain.',
    will_delete: 'This will permanently delete:',
    profile_and_account: '• Your profile and account information',
    meetings_recordings: '• All your meetings and recordings',
    voice_profiles: '• Your voice profiles',
    all_data: '• All associated data',
    delete_my_account: 'Delete My Account',
    modal_should_visible: '✓ Modal should be visible now',
    action_cannot_undone: 'This action cannot be undone',
    warning: '⚠️ Warning:',
    will_permanently: 'This will',
    permanently_irreversibly: 'permanently and irreversibly',
    delete_colon: 'delete:',
    your_account_profile: '✗ Your account and profile',
    all_meetings: '✗ All meetings and recordings',
    all_voice_profiles: '✗ All voice profiles',
    all_preferences: '✗ All preferences and settings',
    enter_password_continue: 'Enter your password to continue',
    your_password: 'Your password',
    type_delete_confirm: 'Type',
    delete_caps: 'DELETE',
    to_confirm: 'to confirm',
    type_delete_capital: 'Type DELETE in capital letters',
    deleting: 'Deleting...'
  },
  
  pt: {
    // Common
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Fechar',
    loading: 'Carregando...',
    success: 'Success!',
    error: 'Error',
    
    // Navigation
    home: 'Início',
    settings: 'Configurações',
    profile: 'Perfil',
    logout: 'Sair',
    
    // Settings Page
    settings_title: 'Settings',
    profile_tab: 'Perfil',
    account_tab: 'Conta',
    security_tab: 'Segurança',
    preferences_tab: 'Preferências',
    notifications_tab: 'Notificações',
    audio_tab: 'Áudio e Vídeo',
    danger_tab: 'Zona de Perigo',
    
    // Preferences
    preferences_title: 'Preferências',
    theme_label: 'Tema',
    theme_light: 'Claro',
    theme_dark: 'Escuro',
    theme_auto: 'Automático (Sistema)',
    language_label: 'Language',
    auto_detect_input: 'Automatically detect input language',
    auto_detect_output: 'Automatically detect output language',
    save_preferences: 'Save Preferences',
    preferences_saved: 'Preferences saved successfully!',
    
    // Profile
    profile_title: 'Informações do Perfil',
    full_name: 'Full Name',
    bio: 'Biografia',
    company: 'Empresa',
    job_title: 'Cargo',
    update_profile: 'Atualizar Perfil',
    profile_updated: 'Profile updated successfully!',
    
    // Security
    security_title: 'Segurança',
    change_password: 'Change Password',
    current_password: 'Current Password',
    new_password: 'New Password',
    confirm_password: 'Confirm New Password',
    password_changed: 'Password changed successfully!',
    two_factor_auth: 'Autenticação de Dois Fatores',
    enable_2fa: 'Ativar 2FA',
    
    // Danger Zone
    danger_title: 'Zona de Perigo',
    delete_account: 'Delete Account',
    delete_account_warning: 'After deleting your account, there is no going back. Please be certain.',
    delete_forever: 'Delete Permanently',
    
    // Notifications
    notifications_title: 'Notification Settings',
    email_notifications: 'Email Notifications',
    push_notifications: 'Notificações Push',
    meeting_reminders: 'Lembretes de Reunião',
    new_features: 'Novos Recursos',
    
    // Audio
    audio_title: 'Audio and Video Settings',
    microphone_volume: 'Volume do Microfone',
    speaker_volume: 'Volume do Alto-falante',
    echo_cancellation: 'Cancelamento de Eco',
    noise_suppression: 'Supressão de Ruído'
  },
  
  fr: {
    ...settingsTranslations.fr,
    ...homeTranslations.fr,
    // Common
    save: 'Enregistrer',
    cancel: 'Annuler',
    delete: 'Supprimer',
    edit: 'Modifier',
    close: 'Fermer',
    loading: 'Chargement...',
    success: 'Succès!',
    error: 'Erreur',
    
    // Navigation
    home: 'Accueil',
    settings: 'Paramètres',
    profile: 'Profil',
    logout: 'Se déconnecter',
    
    // Settings Page
    settings_title: 'Paramètres',
    profile_tab: 'Profil',
    account_tab: 'Compte',
    security_tab: 'Sécurité',
    preferences_tab: 'Préférences',
    notifications_tab: 'Notifications',
    audio_tab: 'Audio et Vidéo',
    danger_tab: 'Zone de Danger',
    
    // Preferences
    preferences_title: 'Préférences',
    theme_label: 'Thème',
    theme_light: 'Clair',
    theme_dark: 'Sombre',
    theme_auto: 'Automatique (Système)',
    language_label: 'Langue',
    auto_detect_input: 'Détecter automatiquement la langue d\'entrée',
    auto_detect_output: 'Détecter automatiquement la langue de sortie',
    save_preferences: 'Enregistrer les Préférences',
    preferences_saved: 'Préférences enregistrées avec succès!',
    
    // Profile
    profile_title: 'Informations du Profil',
    full_name: 'Nom Complet',
    bio: 'Biographie',
    company: 'Entreprise',
    job_title: 'Poste',
    update_profile: 'Mettre à Jour le Profil',
    profile_updated: 'Profil mis à jour avec succès!',
    
    // Security
    security_title: 'Sécurité',
    change_password: 'Changer le Mot de Passe',
    current_password: 'Mot de Passe Actuel',
    new_password: 'Nouveau Mot de Passe',
    confirm_password: 'Confirmer le Nouveau Mot de Passe',
    password_changed: 'Mot de passe changé avec succès!',
    two_factor_auth: 'Authentification à Deux Facteurs',
    enable_2fa: 'Activer 2FA',
    
    // Danger Zone
    danger_title: 'Zone de Danger',
    delete_account: 'Supprimer le Compte',
    delete_account_warning: 'Une fois votre compte supprimé, il n\'y a pas de retour en arrière. Soyez certain.',
    delete_forever: 'Supprimer Définitivement',
    
    // Notifications
    notifications_title: 'Paramètres de Notification',
    email_notifications: 'Notifications par Email',
    push_notifications: 'Notifications Push',
    meeting_reminders: 'Rappels de Réunion',
    new_features: 'Nouvelles Fonctionnalités',
    
    // Audio
    audio_title: 'Paramètres Audio et Vidéo',
    microphone_volume: 'Volume du Microphone',
    speaker_volume: 'Volume du Haut-parleur',
    echo_cancellation: 'Annulation d\'Écho',
    noise_suppression: 'Suppression du Bruit'
  },
  
  es: {
    // Common
    save: 'Guardar',
    cancel: 'Cancelar',
    delete: 'Eliminar',
    edit: 'Editar',
    close: 'Cerrar',
    loading: 'Cargando...',
    success: '¡Éxito!',
    error: 'Error',
    
    // Navigation
    home: 'Inicio',
    settings: 'Configuración',
    profile: 'Perfil',
    logout: 'Cerrar Sesión',
    
    // Settings Page
    settings_title: 'Configuración',
    profile_tab: 'Perfil',
    account_tab: 'Cuenta',
    security_tab: 'Seguridad',
    preferences_tab: 'Preferencias',
    notifications_tab: 'Notificaciones',
    audio_tab: 'Audio y Video',
    danger_tab: 'Zona de Peligro',
    
    // Preferences
    preferences_title: 'Preferencias',
    theme_label: 'Tema',
    theme_light: 'Claro',
    theme_dark: 'Oscuro',
    theme_auto: 'Automático (Sistema)',
    language_label: 'Idioma',
    auto_detect_input: 'Detectar automáticamente el idioma de entrada',
    auto_detect_output: 'Detectar automáticamente el idioma de salida',
    save_preferences: 'Guardar Preferencias',
    preferences_saved: '¡Preferencias guardadas con éxito!',
    
    // Profile
    profile_title: 'Información del Perfil',
    full_name: 'Nombre Completo',
    bio: 'Biografía',
    company: 'Empresa',
    job_title: 'Cargo',
    update_profile: 'Actualizar Perfil',
    profile_updated: '¡Perfil actualizado con éxito!',
    
    // Security
    security_title: 'Seguridad',
    change_password: 'Cambiar Contraseña',
    current_password: 'Contraseña Actual',
    new_password: 'Nueva Contraseña',
    confirm_password: 'Confirmar Nueva Contraseña',
    password_changed: '¡Contraseña cambiada con éxito!',
    two_factor_auth: 'Autenticación de Dos Factores',
    enable_2fa: 'Activar 2FA',
    
    // Danger Zone
    danger_title: 'Zona de Peligro',
    delete_account: 'Eliminar Cuenta',
    delete_account_warning: 'Una vez que elimines tu cuenta, no hay vuelta atrás. Por favor, estate seguro.',
    delete_forever: 'Eliminar Permanentemente',
    
    // Notifications
    notifications_title: 'Configuración de Notificaciones',
    email_notifications: 'Notificaciones por Correo',
    push_notifications: 'Notificaciones Push',
    meeting_reminders: 'Recordatorios de Reunión',
    new_features: 'Nuevas Funcionalidades',
    
    // Audio
    audio_title: 'Configuración de Audio y Video',
    microphone_volume: 'Volumen del Micrófono',
    speaker_volume: 'Volumen del Altavoz',
    echo_cancellation: 'Cancelación de Eco',
    noise_suppression: 'Supresión de Ruido'
  },
  
  de: {
    // Common
    save: 'Speichern',
    cancel: 'Abbrechen',
    delete: 'Löschen',
    edit: 'Bearbeiten',
    close: 'Schließen',
    loading: 'Laden...',
    success: 'Erfolg!',
    error: 'Fehler',
    
    // Navigation
    home: 'Startseite',
    settings: 'Einstellungen',
    profile: 'Profil',
    logout: 'Abmelden',
    
    // Settings Page
    settings_title: 'Einstellungen',
    profile_tab: 'Profil',
    account_tab: 'Konto',
    security_tab: 'Sicherheit',
    preferences_tab: 'Einstellungen',
    notifications_tab: 'Benachrichtigungen',
    audio_tab: 'Audio und Video',
    danger_tab: 'Gefahrenzone',
    
    // Preferences
    preferences_title: 'Einstellungen',
    theme_label: 'Thema',
    theme_light: 'Hell',
    theme_dark: 'Dunkel',
    theme_auto: 'Automatisch (System)',
    language_label: 'Sprache',
    auto_detect_input: 'Eingabesprache automatisch erkennen',
    auto_detect_output: 'Ausgabesprache automatisch erkennen',
    save_preferences: 'Einstellungen Speichern',
    preferences_saved: 'Einstellungen erfolgreich gespeichert!',
    
    // Profile
    profile_title: 'Profilinformationen',
    full_name: 'Vollständiger Name',
    bio: 'Biografie',
    company: 'Unternehmen',
    job_title: 'Berufsbezeichnung',
    update_profile: 'Profil Aktualisieren',
    profile_updated: 'Profil erfolgreich aktualisiert!',
    
    // Security
    security_title: 'Sicherheit',
    change_password: 'Passwort Ändern',
    current_password: 'Aktuelles Passwort',
    new_password: 'Neues Passwort',
    confirm_password: 'Neues Passwort Bestätigen',
    password_changed: 'Passwort erfolgreich geändert!',
    two_factor_auth: 'Zwei-Faktor-Authentifizierung',
    enable_2fa: '2FA Aktivieren',
    
    // Danger Zone
    danger_title: 'Gefahrenzone',
    delete_account: 'Konto Löschen',
    delete_account_warning: 'Sobald Sie Ihr Konto löschen, gibt es kein Zurück mehr. Bitte seien Sie sich sicher.',
    delete_forever: 'Endgültig Löschen',
    
    // Notifications
    notifications_title: 'Benachrichtigungseinstellungen',
    email_notifications: 'E-Mail-Benachrichtigungen',
    push_notifications: 'Push-Benachrichtigungen',
    meeting_reminders: 'Besprechungserinnerungen',
    new_features: 'Neue Funktionen',
    
    // Audio
    audio_title: 'Audio- und Videoeinstellungen',
    microphone_volume: 'Mikrofonlautstärke',
    speaker_volume: 'Lautsprecherlautstärke',
    echo_cancellation: 'Echounterdrückung',
    noise_suppression: 'Rauschunterdrückung'
  }
};

export type Language = keyof typeof translations;
export type TranslationKey = keyof typeof translations.en;
