/**
 * AnalyticsTracker Component
 * Advanced analytics tracking for user behavior and performance
 */
// AnalyticsTracker - No React import needed for this utility class

export interface AnalyticsEvent {
  event: string;
  properties?: Record<string, any>;
  timestamp?: string;
  userId?: string;
  sessionId?: string;
}

class AnalyticsTracker {
  private static instance: AnalyticsTracker;
  private events: AnalyticsEvent[] = [];
  private sessionId: string;
  private userId: string | undefined = undefined;
  private isEnabled: boolean = false; // Disabled - backend endpoints not implemented

  private constructor() {
    this.sessionId = this.generateSessionId();
    this.loadUserId();
    this.setupAutoFlush();
  }

  public static getInstance(): AnalyticsTracker {
    if (!AnalyticsTracker.instance) {
      AnalyticsTracker.instance = new AnalyticsTracker();
    }
    return AnalyticsTracker.instance;
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private loadUserId(): void {
    this.userId = localStorage.getItem('orbis_user_id') || undefined;
  }

  private setupAutoFlush(): void {
    // Flush events every 30 seconds
    setInterval(() => {
      this.flush();
    }, 30000);

    // Flush events before page unload
    window.addEventListener('beforeunload', () => {
      this.flush(true);
    });
  }

  public track(event: string, properties?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const analyticsEvent: AnalyticsEvent = {
      event,
      properties: {
        ...properties,
        url: window.location.href,
        userAgent: navigator.userAgent,
        screenResolution: `${screen.width}x${screen.height}`,
        viewportSize: `${window.innerWidth}x${window.innerHeight}`,
        connectionType: (navigator as any).connection?.effectiveType || 'unknown',
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      },
      timestamp: new Date().toISOString(),
      userId: this.userId,
      sessionId: this.sessionId
    };

    this.events.push(analyticsEvent);

    // Send critical events immediately
    if (this.isCriticalEvent(event)) {
      this.sendEvent(analyticsEvent);
    }

    // Log to console in development
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      console.log('Analytics Event:', analyticsEvent);
    }
  }

  private isCriticalEvent(event: string): boolean {
    const criticalEvents = [
      'user_signup',
      'user_login',
      'meeting_created',
      'meeting_joined',
      'payment_completed',
      'error_occurred'
    ];
    return criticalEvents.includes(event);
  }

  private async sendEvent(event: AnalyticsEvent): Promise<void> {
    try {
      // Send to multiple analytics providers
      await Promise.allSettled([
        this.sendToOrbisAPI(event),
        this.sendToGoogleAnalytics(event),
        this.sendToMixpanel(event)
      ]);
    } catch (error) {
      console.error('Failed to send analytics event:', error);
    }
  }

  private async sendToOrbisAPI(event: AnalyticsEvent): Promise<void> {
    const response = await fetch('/api/analytics/track', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event)
    });

    if (!response.ok) {
      throw new Error(`Analytics API error: ${response.status}`);
    }
  }

  private async sendToGoogleAnalytics(event: AnalyticsEvent): Promise<void> {
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', event.event, {
        event_category: 'orbis',
        event_label: event.event,
        custom_map: event.properties
      });
    }
  }

  private async sendToMixpanel(event: AnalyticsEvent): Promise<void> {
    if (typeof window !== 'undefined' && (window as any).mixpanel) {
      (window as any).mixpanel.track(event.event, event.properties);
    }
  }

  public async flush(sync: boolean = false): Promise<void> {
    if (this.events.length === 0) return;

    const eventsToSend = [...this.events];
    this.events = [];

    try {
      if (sync) {
        // Send synchronously for page unload
        await fetch('/api/analytics/batch', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ events: eventsToSend }),
          keepalive: true
        });
      } else {
        // Send asynchronously
        this.sendBatch(eventsToSend);
      }
    } catch (error) {
      console.error('Failed to flush analytics events:', error);
      // Re-add events to queue if they failed to send
      this.events.unshift(...eventsToSend);
    }
  }

  private async sendBatch(events: AnalyticsEvent[]): Promise<void> {
    try {
      await fetch('/api/analytics/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ events })
      });
    } catch (error) {
      console.error('Failed to send analytics batch:', error);
    }
  }

  public setUserId(userId: string): void {
    this.userId = userId;
    localStorage.setItem('orbis_user_id', userId);
  }

  public setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  public getSessionId(): string {
    return this.sessionId;
  }

  public getUserId(): string | undefined {
    return this.userId;
  }

  // Performance tracking
  public trackPerformance(metric: string, value: number, unit: string = 'ms'): void {
    this.track('performance_metric', {
      metric,
      value,
      unit,
      timestamp: performance.now()
    });
  }

  // Error tracking
  public trackError(error: Error, context?: Record<string, any>): void {
    this.track('error_occurred', {
      error_message: error.message,
      error_stack: error.stack,
      error_name: error.name,
      context
    });
  }

  // User interaction tracking
  public trackInteraction(element: string, action: string, properties?: Record<string, any>): void {
    this.track('user_interaction', {
      element,
      action,
      ...properties
    });
  }

  // Meeting analytics
  public trackMeetingEvent(event: string, roomId: string, properties?: Record<string, any>): void {
    this.track(`meeting_${event}`, {
      room_id: roomId,
      ...properties
    });
  }

  // Voice cloning analytics
  public trackVoiceEvent(event: string, properties?: Record<string, any>): void {
    this.track(`voice_${event}`, properties);
  }

  // Translation analytics
  public trackTranslationEvent(event: string, properties?: Record<string, any>): void {
    this.track(`translation_${event}`, properties);
  }
}

// Export singleton instance
export const analyticsTracker = AnalyticsTracker.getInstance();

// Convenience functions
export const track = (event: string, properties?: Record<string, any>) => {
  analyticsTracker.track(event, properties);
};

export const trackPerformance = (metric: string, value: number, unit?: string) => {
  analyticsTracker.trackPerformance(metric, value, unit);
};

export const trackError = (error: Error, context?: Record<string, any>) => {
  analyticsTracker.trackError(error, context);
};

export const trackInteraction = (element: string, action: string, properties?: Record<string, any>) => {
  analyticsTracker.trackInteraction(element, action, properties);
};

// React hook for analytics
export const useAnalytics = () => {
  return {
    track: analyticsTracker.track.bind(analyticsTracker),
    trackPerformance: analyticsTracker.trackPerformance.bind(analyticsTracker),
    trackError: analyticsTracker.trackError.bind(analyticsTracker),
    trackInteraction: analyticsTracker.trackInteraction.bind(analyticsTracker),
    trackMeetingEvent: analyticsTracker.trackMeetingEvent.bind(analyticsTracker),
    trackVoiceEvent: analyticsTracker.trackVoiceEvent.bind(analyticsTracker),
    trackTranslationEvent: analyticsTracker.trackTranslationEvent.bind(analyticsTracker),
    setUserId: analyticsTracker.setUserId.bind(analyticsTracker),
    setEnabled: analyticsTracker.setEnabled.bind(analyticsTracker)
  };
};

// Global error handler
window.addEventListener('error', (event) => {
  analyticsTracker.trackError(event.error, {
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno
  });
});

window.addEventListener('unhandledrejection', (event) => {
  analyticsTracker.trackError(new Error(event.reason), {
    type: 'unhandled_promise_rejection'
  });
});

// Performance observer
if ('PerformanceObserver' in window) {
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.entryType === 'navigation') {
        const navEntry = entry as PerformanceNavigationTiming;
        analyticsTracker.trackPerformance('page_load_time', navEntry.loadEventEnd - navEntry.fetchStart);
        analyticsTracker.trackPerformance('dom_content_loaded', navEntry.domContentLoadedEventEnd - navEntry.fetchStart);
        analyticsTracker.trackPerformance('first_paint', navEntry.responseEnd - navEntry.fetchStart);
      }
    }
  });
  
  observer.observe({ entryTypes: ['navigation'] });
}

export default AnalyticsTracker;

