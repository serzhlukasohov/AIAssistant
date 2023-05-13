import os
import shutil

def main():
    # Modify the source directory path according to your needs
    source_dir = './test'

    # Modify the output directory path according to your needs
    output_dir = './output'

    # Modify the file types you want to process
    file_types = ('.md', '.js', '.ts', '.json', '.sql')

    # Initialize the variable for the README.md file
    readme_file = None

    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Walk through the source directory to find files with the specified file types
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_types) and file != 'README.md':
                # Create the input and output file paths
                input_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_file_path, source_dir)
                new_root = root.replace(source_dir, output_dir)
                output_file_path = os.path.join(new_root, f'{os.path.splitext(file)[0]}.{os.path.splitext(file)[1][1:]}.txt')

                # Create the output directory if it doesn't exist
                if not os.path.exists(new_root):
                    os.makedirs(new_root)

                # Read the input file and write the output file with custom text
                with open(input_file_path, 'r', encoding='ISO-8859-1') as infile, open(output_file_path, 'w', encoding='ISO-8859-1') as outfile:
                    # Change the message here if needed
                    outfile.write(f'This is a txt representation of the VirtueMaster file located at {relative_path}\n\n')
                    outfile.write(infile.read())

            # Process the README.md file separately
            elif file == 'README.md':
                readme_input_file_path = os.path.join(root, file)
                readme_relative_path = os.path.relpath(readme_input_file_path, source_dir)

    # Convert the README.md file to a txt file
    if readme_file:
        readme_new_root = readme_input_file_path.replace(source_dir, output_dir)
        readme_output_file_path = os.path.join(os.path.dirname(readme_new_root), f'{os.path.splitext("README.md")[0]}.{os.path.splitext("README.md")[1][1:]}.txt')
        with open(readme_input_file_path, 'r', encoding='ISO-8859-1') as infile, open(readme_output_file_path, 'w', encoding='ISO-8859-1') as outfile:
            # Change the message here if needed
            outfile.write(f'This is a txt representation of the VirtueMaster file located at {readme_relative_path}\n\n')
            outfile.write(infile.read())

if __name__ == '__main__':
    main()