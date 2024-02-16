import React from 'react';

const CodeEditor = ({logs}) => {
    return (
        <div className="bg-black bg-opacity-75 rounded-lg p-4 mt-6">
            <div className="flex justify-between text-xs text-gray-400 mb-2">
                <div>Movie Agent Logs</div>
                <div>SITE = StackAPI('stackoverflow')</div>
            </div>
            <div className="text-xs leading-tight">
                {logs}
            </div>
        </div>
    );
};

export default CodeEditor;