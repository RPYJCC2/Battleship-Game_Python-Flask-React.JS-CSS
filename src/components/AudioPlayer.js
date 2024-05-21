import React, { useEffect, useState } from 'react';

const AudioPlayer = () => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [audio, setAudio] = useState(null);

    useEffect(() => {
        const audioElement = document.createElement("audio");
        audioElement.id = "radioChatter";
        audioElement.loop = true;
        audioElement.volume = 0.5;
        audioElement.src = process.env.PUBLIC_URL + "/audio/radio_chatter.mp3";
        audioElement.type = "audio/mpeg";
        document.body.appendChild(audioElement);
        setAudio(audioElement);

        // Attempt to autoplay
        audioElement.play().then(() => {
            console.log('Audio is playing automatically');
            setIsPlaying(true);
        }).catch(error => {
            console.log('Autoplay was prevented:', error);
            setIsPlaying(false);
        });

        // Cleanup function to remove the audio element when the component unmounts
        return () => {
            audioElement.pause();
            document.body.removeChild(audioElement);
        };
    }, []);

    const toggleAudio = () => {
        if (audio) {
            if (isPlaying) {
                audio.pause();
                setIsPlaying(false);
            } else {
                audio.play().then(() => {
                    setIsPlaying(true);
                }).catch(error => {
                    console.error('Error playing audio:', error);
                });
            }
        }
    };

    return (
        <div>
            <button onClick={toggleAudio}>
                {isPlaying ? 'Pause Radio Chatter' : 'Play Radio Chatter'}
            </button>
        </div>
    );
};

export default AudioPlayer;
