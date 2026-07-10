# Interview Agent Frontend Integration Guide

This guide is for the frontend developer integrating the live Video/Voice Interview agent.

## Architecture Overview
To achieve sub-second latency for a live conversational AI without incurring massive API costs for Text-to-Speech (TTS) and Speech-to-Text (STT), we are leveraging **Native Browser APIs**.

- **Backend**: FastAPI server hosting a WebSocket endpoint (`/ws/interview`). It handles the conversation memory and streams responses from the Fireworks LLM.
- **Frontend**: Handles the camera feed (for visual UX), uses `SpeechRecognition` to transcribe the user's voice to text, and `speechSynthesis` to speak the AI's responses out loud.

## The Workflow

1. **Connect to WebSocket**: Connect to `ws://[BACKEND_IP]:8000/ws/interview`.
2. **Initialize Camera**: Use `navigator.mediaDevices.getUserMedia({ video: true })` and attach it to a `<video>` element on the screen.
3. **Start Interview**: 
   - When the user is ready, send a trigger message (e.g., `"READY"`) to the WebSocket.
   - The backend will stream the AI's first question as text chunks.
4. **AI Speaking (TTS)**:
   - Accumulate the text chunks coming from the WebSocket.
   - When the backend sends `[END_OF_TURN]`, pass the accumulated text to `window.speechSynthesis.speak()`.
5. **User Speaking (STT)**:
   - When the TTS finishes speaking (`utterance.onend`), immediately start `window.SpeechRecognition`.
   - When the user stops speaking, the API will trigger `recognition.onresult`. Take that transcribed text and send it through the WebSocket to the backend.
   - The backend will process the text and stream back the next AI response.
6. **Loop**: Repeat steps 4 and 5 until the interview concludes.

## Code Example
We have provided a fully working, vanilla HTML/JS implementation of this exact architecture. 

Please see **`agent2/test_client.html`** in this repository. You can literally double-click it in your browser (while the FastAPI server is running) to experience the full video call AI interview. You can copy the JavaScript logic directly into your React/Vue/Angular frontend.
