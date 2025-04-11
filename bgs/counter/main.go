package main

func main() {
	// Init mic listener
	InitPortAudio()
	defer TerminatePortAudio()

	for {
		if VoiceDetected() {
			audio := RecordAudioSession()
			text := TranscribeAudio(audio)
			println("Transcript:", text)
		}
	}
}
