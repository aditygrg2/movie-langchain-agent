import React, { useEffect, useState } from "react";
import { VscCircleLargeFilled } from "react-icons/vsc";
import { BsArrowDownCircleFill, BsArrowUpCircleFill } from "react-icons/bs";
import SyntaxHighlighter from "react-syntax-highlighter";
import { xt256 } from "react-syntax-highlighter/dist/esm/styles/hljs";
import _ from "lodash";
import { agentStatus } from "./App";
import { motion, AnimatePresence } from "framer-motion";

const status_color_map = {
  1: "green",
  2: "red",
  3: "yellow",
};

const status_text_map = {
  1: "Live",
  2: "Offline",
  3: "Working",
};

const CodeEditor = ({
  socket,
  setLogs,
  logs,
  setAnswer,
  status,
  setStatus,
  setQuery,
}) => {
  const [code, setCode] = useState("");
  const [toggleLogs, setToggleLogs] = useState(false);

  useEffect(() => {
    if (status === agentStatus.WORKING) {
      setToggleLogs(true);
    }
  }, [status]);

  useEffect(() => {
    setCode(JSON.stringify(logs, null, 2));
  }, [logs]);

  useEffect(() => {
    socket.on("agent_log", (log) => {
      const dict_log = convert_log_to_dict(log);

      setLogs((prev_logs) => [...prev_logs, dict_log]);
    });

    socket.on("final_answer", (ans) => {
      setLogs((prev_logs) => [
        ...prev_logs,
        {
          response: ans,
        },
      ]);

      setAnswer((prev_ans) => {
        return {
          ...prev_ans,
          answer: ans,
        };
      });

      if (socket && socket.connected) {
        setStatus(agentStatus.LIVE);
      } else {
        setStatus(agentStatus.OFFLINE);
      }

      setToggleLogs(false);
    });
  }, []);

  const convert_log_to_dict = (input) => {
    const pattern = /(\w+)\s*=\s*'([^']*)'/g;

    const keyValuePairs = {};

    let match;
    while ((match = pattern.exec(input)) !== null) {
      const key = match[1];
      const value = match[2];
      keyValuePairs[key] = value;
    }

    return keyValuePairs;
  };

  const handleToggleLogs = () => {
    setToggleLogs((t) => !t);
  };

  return (
    <div className="bg-black bg-opacity-75 rounded-lg mt-6 flex flex-col overflow-scroll max-h-80">
      <div className="flex justify-between text-xs text-gray-400 p-4 sticky">
        <div className="flex gap-x-2">
          {!toggleLogs ? (
            <BsArrowUpCircleFill
              size={16}
              className="z-2 fill-slate-100 inline"
              onClick={handleToggleLogs}
            ></BsArrowUpCircleFill>
          ) : (
            <BsArrowDownCircleFill
              size={16}
              className="z-2 fill-slate-100 inline"
              onClick={handleToggleLogs}
            ></BsArrowDownCircleFill>
          )}
          <p>Movie Agent Logs</p>
        </div>
        <div className="">
          Agent Status: {status_text_map[status]}
          <span className="p-1">
            <VscCircleLargeFilled
              color={status_color_map[status]}
              size={15}
              className={"inline animate-pulse"}
            />
          </span>
        </div>
      </div>

      <AnimatePresence>
        {toggleLogs && (
          <motion.div
            key="toggle"
            initial={{ height: 0 }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            transition={{ duration: 0.5 }}
          >
            <SyntaxHighlighter
              language="javascript"
              style={xt256}
              showLineNumbers={true}
              className={
                "flex flex-col grow text-sm leading-tight bg-black rounded-lg p-2 m-2"
              }
              wrapLines={true}
            >
              {code}
            </SyntaxHighlighter>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CodeEditor;
