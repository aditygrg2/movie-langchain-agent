import React, { useEffect, useState, useRef, useCallback } from "react";
import CodeEditor from "./CodeEditor";
import _ from "lodash";
import { RiMovie2Fill } from "react-icons/ri";
import { motion, AnimatePresence } from "framer-motion";
import { PiFilmSlateBold } from "react-icons/pi";

export const agentStatus = {
  LIVE: 1,
  OFFLINE: 2,
  WORKING: 3,
};

const App = ({ socket }) => {
  const inputRef = useRef();
  const [status, setStatus] = useState(agentStatus.OFFLINE);
  const [logs, setLogs] = useState([]);
  const [answer, setAnswer] = useState({
    image: "",
    answer: "",
  });
  const [query, setQuery] = useState("");

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
    const q = inputRef?.current?.value;
    if (status === agentStatus.LIVE && q && q.length > 0) {
      setQuery(q);
      setAnswer({ answer: "", image: "" });

      socket.emit("message", q);

      setStatus(agentStatus.WORKING);
      setLogs((prev_logs) => [
        ...prev_logs,
        {
          query: q,
        },
      ]);

      inputRef.current.value = "";
    } else if (status === agentStatus.WORKING) {
    } else {
      setQuery(q);
      setAnswer({
        answer:
          "We are trying to connect to agent. Please try again once we are up! Sorry for the inconvenience.",
        image:
          "https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/9d8aad33437265.5ba16b3b9472c.jpg",
      });
    }
  };

  return (
    <div className="mx-auto p-6 bg-gradient-to-r from-rose-400 via-fuchsia-500 to-indigo-500 text-white w-screen min-h-screen flex flex-col">
      <div className="bg-black bg-opacity-50 rounded-lg p-4 flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <div className="text-3xl antialiased hover:subpixel-antialiased"><PiFilmSlateBold className="inline p-1 hover:fill-pink-500"></PiFilmSlateBold>Cinematica</div>
          <div className="text-sm">
            <a
              target="_blank"
              href="https://rapidapi.com/apidojo/api/imdb8"
              className="decoration-sky-500 underline"
            >
              powered by IMDb API
            </a>
            <sup>TM</sup>
          </div>
        </div>

        <div className="flex flex-col justify-center m-10 gap-y-2">
          <h1 className="text-3xl font-bold text-start antialiased pb-4">Ask me about movies, actors or anything from IMDb powered by LLM</h1>
          <h6 className="text-md text-slate-200 text-start">
            How much money did Avengers Endgame made?
          </h6>
          <div className="flex w-full gap-x-2">
            <input
              className="rounded-xl p-3 text-black grow border-2 bg-slate-100 active:border-4 select:border-pink-500 disabled:bg-slate-400"
              placeholder="Get answers about everything from IMDb, just ask!"
              ref={inputRef}
              disabled={status === agentStatus.WORKING}
              onKeyDown={(e) => {
                if (e.repeat) return;

                if (e.key == "Enter" && agentStatus.LIVE == status) {
                  handleQuery();
                }
              }}
            ></input>
            <div className="relative">
              <RiMovie2Fill
                className={`cursor-pointer ${
                  status === agentStatus.WORKING
                    ? "animate-spin"
                    : " w-full h-full self-center"
                }`}
                onClick={handleQuery}
                color="pink"
                size={40}
              ></RiMovie2Fill>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {query && query.length > 0 && (
            <motion.div
              key="query"
              initial={{ height: 0 }}
              animate={{ height: "auto" }}
              exit={{ height: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="space-y-4">
                <p className="font-bold text-lg text-center">{query}</p>
                {answer["answer"] && answer["answer"].length <= 0 && (
                  <div
                    className={
                      "text-center flex items-center justify-center p-2 text-lg font-semibold text-wrap select-all selection:bg-yellow-300 selection:text-black"
                    }
                  >
                    {"Thinking..."}
                  </div>
                )}
                <AnimatePresence>
                  {
                    <motion.div
                      key="ans"
                      initial={{ height: 0 }}
                      animate={{ height: "auto" }}
                      exit={{ height: 0 }}
                      transition={{ duration: 0.5 }}
                      className="flex"
                    >
                      {answer["answer"] && answer["answer"].length > 0 && (
                        <div
                          className={
                            "text-center flex items-center justify-center p-2 text-lg font-semibold text-wrap select-all selection:bg-yellow-300 selection:text-black w-[70%]"
                          }
                        >
                          {answer["answer"]}
                        </div>
                      )}
                      {answer["answer"] && answer["image"] && answer["answer"].length > 0 && answer["image"]?.length > 0 && (
                        <div className="flex justify-center items-center grow">
                          <img className="max-h-60 max-w-60" src={answer['image']}></img>
                        </div>
                      )}
                    </motion.div>
                  }
                </AnimatePresence>
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
        setQuery={setQuery}
      />
    </div>
  );
};

export default App;
