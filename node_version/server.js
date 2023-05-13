const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const folderName = 'test';

const currentDir = process.cwd();

const newFolderPath = path.join(currentDir, folderName);

if (!fs.existsSync(newFolderPath)) {
  fs.mkdirSync(newFolderPath);
}

const hostName = 'localhost';
const serverPort = 8080;

const server = http.createServer((req, res) => {
  const { url } = req;
  const params = {};
  let responseText = '{"downloaded": true}';

  if (url.includes('?')) {
    const [path, queryString] = url.split('?');
    const queryParameters = queryString.split('&');

    queryParameters.forEach((param) => {
      const [key, value] = param.split('=');
      params[key] = value;
    });
  }

  if (params.git) {
    const gitFolderName = params.git.split('/').pop();
    const gitFolderPath = path.join(currentDir, folderName, gitFolderName);

    if (!fs.existsSync(gitFolderPath)) {
      const gitProcess = spawn('git', ['clone', `https://github.com/${params.git}`, gitFolderPath]);
      gitProcess.on('close', (code) => {
        if (code === 0) {
          txtFormatter(gitFolderName);
          responseText = `{"Success": ${getAnswer(gitFolderName)}}`;
        } else {
          responseText = '{"something_wrong": true}';
        }
        res.statusCode = 200;
        res.setHeader('Content-Type', 'application/json');
        res.end(responseText);
      });
      return;
    } else {
      txtFormatter(gitFolderName);
      responseText = `{"Success": ${getAnswer(gitFolderName)}}`;
    }
  } else {
    responseText = '{"something_wrong": true}';
  }

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.end(responseText);
});

server.listen(serverPort, hostName, () => {
  console.log(`Server started http://${hostName}:${serverPort}`);
});

process.on('SIGINT', () => {
  server.close(() => {
    console.log('Server stopped.');
    process.exit();
  });
});