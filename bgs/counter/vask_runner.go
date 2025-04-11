// vosk_runner.go
package main

import (
	"fmt"
	"os/exec"
	"strings"
)

func TranscribeAudio(filename string) string {
	out, err := exec.Command("python3", "vosk_transcribe.py", filename).Output()
	if err != nil {
		fmt.Println("Transcription error:", err)
		return ""
	}
	return strings.TrimSpace(string(out))
}
