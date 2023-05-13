const fs = require('fs');
const path = require('path');

function main() {
  // Modify the source directory path according to your needs
  const sourceDir = './test';

  // Modify the output directory path according to your needs
  const outputDir = './output';

  // Modify the file types you want to process
  const fileTypes = ['.md', '.js', '.ts', '.json', '.sql'];

  // Check if the output directory exists, if not, create it
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Walk through the source directory to find files with the specified file types
  const files = getFilesRecursive(sourceDir, fileTypes);

  // Process each file
  files.forEach((file) => {
    const inputFilePath = file;
    const relativePath = path.relative(sourceDir, inputFilePath);
    const newRoot = path.dirname(inputFilePath.replace(sourceDir, outputDir));
    const outputFile = path.join(
      newRoot,
      `${path.parse(file).name}.${path.parse(file).ext.slice(1)}.txt`
    );

    // Create the output directory if it doesn't exist
    if (!fs.existsSync(newRoot)) {
      fs.mkdirSync(newRoot, { recursive: true });
    }

    // Read the input file and write the output file with custom text
    const fileContent = fs.readFileSync(inputFilePath, 'utf8');
    const outputContent = `This is a txt representation of the VirtueMaster file located at ${relativePath}\n\n${fileContent}`;
    fs.writeFileSync(outputFile, outputContent, 'utf8');
  });

  // Process the README.md file separately
  const readmeFile = files.find((file) => path.basename(file) === 'README.md');
  if (readmeFile) {
    const readmeInputFilePath = readmeFile;
    const readmeRelativePath = path.relative(sourceDir, readmeInputFilePath);
    const readmeOutputFile = path.join(
      path.dirname(readmeInputFilePath.replace(sourceDir, outputDir)),
      `${path.parse('README.md').name}.${path.parse('README.md').ext.slice(1)}.txt`
    );

    // Read the README.md file and write the output file with custom text
    const readmeContent = fs.readFileSync(readmeInputFilePath, 'utf8');
    const outputContent = `This is a txt representation of the VirtueMaster file located at ${readmeRelativePath}\n\n${readmeContent}`;
    fs.writeFileSync(readmeOutputFile, outputContent, 'utf8');
  }
}

function getFilesRecursive(dir, fileTypes) {
  let files = [];

  if (!fs.existsSync(dir)) {
    return files;
  }

  const dirEntries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of dirEntries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files = files.concat(getFilesRecursive(fullPath, fileTypes));
    } else if (entry.isFile() && fileTypes.includes(path.extname(fullPath))) {
      files.push(fullPath);
    }
  }

  return files;
}

main();
