// ============================================================================
// frontend/src/components/alerts/VoiceAlert.jsx
// ============================================================================

import React, { useEffect, useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import Button from '../common/Button';
import websocketService from '../../services/websocket';

export default function VoiceAlert() {
  const [enabled, setEnabled] = useState(true);
  const [lastAlert, setLastAlert] = useState(null);

  useEffect(() => {
    websocketService.on('alert', (alert) => {
      if (enabled && alert.severity === 'critical') {
        speakAlert(alert.message);
        setLastAlert(alert);
      }
    });
  }, [enabled]);

  const speakAlert = (message) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const testVoiceAlert = () => {
    speakAlert('This is a test voice alert. Critical event detected.');
  };

  return (
    <div className="flex items-center space-x-2">
      <Button
        variant={enabled ? 'primary' : 'secondary'}
        size="sm"
        onClick={() => setEnabled(!enabled)}
      >
        {enabled ? (
          <>
            <Volume2 className="w-4 h-4 mr-2" />
            Voice Alerts On
          </>
        ) : (
          <>
            <VolumeX className="w-4 h-4 mr-2" />
            Voice Alerts Off
          </>
        )}
      </Button>

      <Button
        variant="outline"
        size="sm"
        onClick={testVoiceAlert}
        disabled={!enabled}
      >
        Test
      </Button>

      {lastAlert && (
        <span className="text-xs text-gray-500">
          Last: {new Date(lastAlert.timestamp).toLocaleTimeString()}
        </span>
      )}
    </div>
  );
}
