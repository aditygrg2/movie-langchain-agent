import React, { useEffect, useState, useRef } from "react";
import CodeEditor from "./CodeEditor";
import _ from "lodash";
import { RiMovie2Fill } from "react-icons/ri";
import { motion, AnimatePresence } from "framer-motion"

export const agentStatus = {
  LIVE: 1,
  OFFLINE: 2,
  WORKING: 3,
};

const App = ({ socket }) => {
  document.addEventListener('keydown', (e) => {
    if(e.keyCode == 13){
      handleQuery();
    }
  })

  const inputRef = useRef();
  const [status, setStatus] = useState(agentStatus.OFFLINE);
  const [logs, setLogs] = useState([]);
  const [answer, setAnswer] = useState({
    image: "",
    answer: "",
  });
  const [query, setQuery] = useState("");
  const id = useRef();

  console.log(socket);

  useEffect(() => {
    socket.connect();

    socket.on("connect", () => {
      setStatus(agentStatus.LIVE);
      setLogs((prev_logs) => [
        ...prev_logs,
        {
          status: "Agent is live!",
        },
      ]);
      console.log("Initial connection started...");
    });

    socket.on("disconnect", () => {
      // send this as message log.
      setLogs((prev_logs) => [
        ...prev_logs,
        {
          status: "Agent is offline!",
        },
      ]);
      setStatus(agentStatus.OFFLINE);
    });

    socket.on("image_query", (image) => {
      setAnswer((ans) => {
        return { answer: ans["answer"], image: image };
      });
    });

    return () => {
      socket.removeAllListeners();
      socket.disconnect();
      setLogs((prev_logs) => [
        ...prev_logs,
        {
          status: "Agent is offline!",
        },
      ]);
      setStatus(agentStatus.OFFLINE);
    };
  }, []);

  const handleQuery = () => {
    id = setTimeout(() => {
      setQuery("")
      setAnswer({
        "answer":"There are some problems in fetching the query. Please try again!",
        "image": ""
      })
    }, 1000*120)

    const q = inputRef.current.value;

    if (q.length == 0) {
      setAnswer({answer: "Thinking...", image: ""})
      return;
    }

    socket.emit("message", q);
    setStatus(agentStatus.WORKING);
    setQuery(q);
    setLogs((prev_logs) => [
      ...prev_logs,
      {
        query: q,
      },
    ]);

    inputRef.current.value = "";
  };

  return (
    <div className="mx-auto p-6 bg-gradient-to-r from-rose-400 via-fuchsia-500 to-indigo-500 text-white h-screen w-screen flex flex-col">
      <div className="bg-black bg-opacity-50 rounded-lg p-4 flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <div className="text-xl">Movie Answering Bot</div>
          <div className="text-sm">
            <a target="_blank" href="https://rapidapi.com/apidojo/api/imdb8">
              powered by IMDb API
            </a>
            <sup>TM</sup>
          </div>
        </div>

        <div className="flex flex-col justify-center m-10 gap-y-2">
          <h1 className="text-3xl font-bold text-start">Ask me about movies</h1>
          <h6 className="text-md text-slate-200 text-start">
            How much money did Avengers Endgame made?
          </h6>
          {/* Make a movies, actor type thing here */}
          <div className="flex w-full gap-x-2">
            <input
              className="rounded-xl p-3 text-black grow border-2 bg-slate-100 active:border-4 select:border-pink-500 disabled:bg-slate-400"
              placeholder="Get answers about everything from IMDb, just ask!"
              ref={inputRef}
              disabled={status === agentStatus.WORKING}
            ></input>
            <div className="h-full relative">
              <RiMovie2Fill
                className={`h-full w-full cursor-pointer ${status === agentStatus.WORKING ? "animate-spin" : ""}`}
                onClick={handleQuery}
                color="pink"
              ></RiMovie2Fill>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {query.length > 0 && (
            <motion.div
            key="query"
            initial={{ height: "0%" }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            transition={{duration: 0.4}}
            >
            <div className="space-y-4">
              <p className="font-bold text-lg">Query: {query}</p>
              {answer["answer"].length > 0 && (
                <div className="flex p-4 items-center justify-center">
                  <p className={answer["image"].length > 0 ? "w-3/4 text-center " : "w-full " + "flex items-center justify-center p-2 text-2xl font-semibold text-wrap select-all selection:bg-yellow-300 selection:text-black"}>
                    {answer["answer"]}
                  </p>
                  {answer["image"].length > 0 && (
                    <div className="flex justify-normal items-center">
                      <img
                        className="w-1/2"
                        src={
                          answer['image']
                        }
                      ></img>
                    </div>
                  )}
                </div>
              )}
            </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <CodeEditor
        socket={socket}
        setLogs={setLogs}
        logs={logs}
        setAnswer={setAnswer}
        status={status}
        setStatus={setStatus}
        ref={id}
      />
    </div>
  );
};

export default App;
