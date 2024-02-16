import React, {useEffect, useState, useRef} from 'react';
import CodeEditor from './CodeEditor';

import io from 'socket.io-client';

const socket = io('http://127.0.0.1:5000');

const App = () => {
    const [query, setQuery] = useState("")
    const [logs, setLogs] = useState("")
    const inputRef = useRef()

    useEffect(() => {
      socket.on('connect', () => {
          console.log('Connected to Flask backend via socket');
      });

      socket.on('message', (message) => {
        setLogs((log) => {
          return log + message
        })
      });

      return () => {
          socket.disconnect();
      };
    }, []);

    const handleQuery = () => {
      console.log(inputRef.current.value)
      socket.emit('message', inputRef.current.value);
    }

    return (
        <div className="mx-auto p-6 bg-gradient-to-r from-rose-400 via-fuchsia-500 to-indigo-500 text-white relative">
            <div className="bg-black bg-opacity-50 rounded-lg p-4">
                <div className="flex justify-between items-center mb-4">
                    <div className="text-xl">Movie Answering Bot</div>
                    <div className="text-sm"><a target='_blank' href='https://rapidapi.com/apidojo/api/imdb8'>powered by IMDb API</a><sup>TM</sup></div>
                </div>

                <div className="flex flex-col justify-center m-20">
                    <h1 className="text-3xl font-bold text-center p-4">Ask anything related to movies here...</h1>
                    {/* Make a movies, actor type thing here */}
                    <input className='rounded-xl p-4 text-black' placeholder='I like Avengers.' ref={inputRef}></input>
                    <button onClick={handleQuery}>Search</button>
                </div>

                {/* <div className="space-y-4">
                    <p>It looks like you're working on software development code, how can I help you?</p>
                    <p>Yes, you're right Libra! I couldn't find my error syntax. I don't know whats wrong, because it won't run smoothly.</p>
                    <p>Your tags is wrong in line 15. Which is syntax "ruby-on-rails" isn't defined as supposed to be. You can fix your code based on defined on the body code. Let me give you example...</p>
                    <div className="bg-purple-800 bg-opacity-50 rounded p-2">
                        <code className="text-pink-300">tags: [<br />
                            "ruby-on-rails",<br />
                            "ipv4",<br />
                            "geokit"<br />
                        ]</code>
                    </div>
                    <p>Wow, now it's work, thanks for helping</p>
                    <p>No problem. Do you wanna learn more about php api integration?</p>
                </div> */}
            </div>
            <CodeEditor logs={logs}/>
        </div>
    );
};

export default App;