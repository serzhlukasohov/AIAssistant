const fs = require('fs');
const dotenv = require('dotenv');
const path = require('path');

const { OpenAI } = require('langchain/llms');
const { RetrievalQAChain } = require('langchain/chains');
const { HNSWLib } = require('langchain/vectorstores');
const { OpenAIEmbeddings } = require('langchain/embeddings');
const { RecursiveCharacterTextSplitter } = require('langchain/text_splitter');
dotenv.config();

const txtFilename = "The_Creative_Act";
const question = "Why they needs it?";
const txtPath = `./${txtFilename}.txt`;
const VECTOR_STORE_PATH = `${txtFilename}.index`;

const runWithEmbeddings = async () => {
  const model = new OpenAI({});
  let vectorStore;
  if (fs.existsSync(VECTOR_STORE_PATH)) {
    console.log('Vector Exists..');
    vectorStore = await HNSWLib.load(VECTOR_STORE_PATH, new OpenAIEmbeddings());
  } else {
    const text = fs.readFileSync(txtPath, 'utf8');
    const textSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000 });
    const docs = await textSplitter.createDocuments([text]);
    vectorStore = await HNSWLib.fromDocuments(docs, new OpenAIEmbeddings());
    await vectorStore.save(VECTOR_STORE_PATH);
  }

  const chain = RetrievalQAChain.fromLLM(model, vectorStore.asRetriever());

  const res = await chain.call({
    query: question,
  });

  console.log({ res });
};

runWithEmbeddings();