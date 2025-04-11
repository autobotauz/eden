// recorder.go
package main

import (
	"bytes"
	"encoding/binary"
	"os"
	"time"

	"github.com/gordonklaus/portaudio"
)

const (
	sampleRate      = 16000
	secondsToRecord = 5
)

func InitPortAudio() {
	portaudio.Initialize()
}

func TerminatePortAudio() {
	portaudio.Terminate()
}

// RecordAudioSession records N seconds and saves to a WAV file.
func RecordAudioSession() string {
	fileName := "recording.wav"

	buffer := make([]int16, 64)
	stream, err := portaudio.OpenDefaultStream(1, 0, sampleRate, len(buffer), buffer)
	if err != nil {
		panic(err)
	}
	defer stream.Close()

	stream.Start()
	defer stream.Stop()

	var audioData []int16
	deadline := time.Now().Add(secondsToRecord * time.Second)

	for time.Now().Before(deadline) {
		if err := stream.Read(); err != nil {
			panic(err)
		}
		audioData = append(audioData, buffer...)
	}

	saveAsWav(fileName, audioData)
	return fileName
}

func saveAsWav(filename string, data []int16) {
	f, err := os.Create(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	// WAV header
	byteRate := sampleRate * 2
	dataLen := len(data) * 2
	header := &bytes.Buffer{}
	header.WriteString("RIFF")
	binary.Write(header, binary.LittleEndian, uint32(36+dataLen))
	header.WriteString("WAVEfmt ")
	binary.Write(header, binary.LittleEndian, uint32(16))
	binary.Write(header, binary.LittleEndian, uint16(1))          // PCM
	binary.Write(header, binary.LittleEndian, uint16(1))          // Mono
	binary.Write(header, binary.LittleEndian, uint32(sampleRate)) // SampleRate
	binary.Write(header, binary.LittleEndian, uint32(byteRate))   // ByteRate
	binary.Write(header, binary.LittleEndian, uint16(2))          // BlockAlign
	binary.Write(header, binary.LittleEndian, uint16(16))         // BitsPerSample
	header.WriteString("data")
	binary.Write(header, binary.LittleEndian, uint32(dataLen))
	f.Write(header.Bytes())

	// Write samples
	binary.Write(f, binary.LittleEndian, data)
}
