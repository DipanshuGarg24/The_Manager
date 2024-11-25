import json
import os

#  meta data me basically
#  find dir
#  find file
#  parent
#  child

class MetadataManager:

    GROUP_N = None
    Groupfile = None
    GROUP_ID = None
    UserID = None
    group_count = 0
    path = None

    # groupmetadata with name mapping
    group_names = {}


    def __init__(self):
        pass

    def rename_file(self):
        pass

    def search_file(self, name):
        """
        Searches for a file by name and returns its file ID if found, otherwise returns -1.

        Args:
            name (str): Name of the file to search for.

        Returns:
            str: File ID if the file is found.
            int: -1 if the file is not found.
        """
        directory_path = f'data/{self.UserID}'
        Groupfile = os.path.join(directory_path, self.Groupfile)

        # Load the current JSON data
        with open(Groupfile, 'r') as f:
            data = json.load(f)

        # Helper function to recursively search for the file
        def _recursive_search(current_dir, target_name):
            if "data" not in current_dir:
                return None
            
            for key, value in current_dir["data"].items():
                if key == target_name and value.get("type") == "file":
                    return value.get("fileid", key)  # Return the file ID or key if no ID is set
                
                if value.get("type") == "dir":
                    result = _recursive_search(value, target_name)
                    if result:
                        return result
            
            return None

        # Start the search from the current path
        target_path = self._sanitize_path(self.path)
        current_dir = self._navigate_to_path(data, target_path)

        if current_dir is None:
            print(f"Invalid current path: '{target_path}'")
            return -1

        # Search for the file
        result = _recursive_search(current_dir, name)
        if result is None:
            print(f"File '{name}' not found.")
            return -1

        print(f"File '{name}' found with ID: {result}")
        return result

    
    def SetActiveUser(self,userid):
        # set the user active :)
        # and also returns all the groups which are connected to it :)

        self.UserID = userid
        directory_path = f'data/{userid}'

        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

        # Initialize an empty dictionary to store filename-title pairs
        file_title_dict = {}
        groups = []
        grpcnt = 0
        # Traverse the directory
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                file_path = os.path.join(directory_path,filename)

                # Open each JSON file and read the title
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    title = data.get("title", "No title found")
                    groups.append((filename,title)) 
                    # Store the title with the filename (without extension) as the key
                    file_title_dict[title] = os.path.splitext(filename)[0]

                grpcnt+=1

        # Print the resulting dictionary
        print(file_title_dict)
        self.group_count = grpcnt
        return groups

    def selectGroup(self,groupfilename,groupname):
        self.Groupfile = groupfilename
        self.GROUP_ID = os.path.splitext(groupfilename)[0]
        self.path = ""
        self.GROUP_N = groupname
        return f"{groupname} has been Selected \nCr Dir : {self.GROUP_N}"
        #  just open that file with the name 

    def AddGroup(self,group_name,userid,groupid):
        '''x = 1 -- channel is new x == 2 channel is already exiisting '''
        # check if the userid directpry exits or not
        if os.path.isdir(f"data/{userid}"):
            if os.path.isfile(f"data/{userid}/{groupid}.json"):
                return 2
        else:
            os.mkdir(f"data/{userid}")
        # create a json file and add the title and keep the data fielld empty
        json_content = {
            "title": group_name,
            "data": {}
        }
        # Specify the file path
        file_path = f'data/{userid}/{groupid}.json'
        # Write the structure to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(json_content, json_file, indent=4)
        return 1
    
    def _sanitize_path(self, input_path):
        """
        Cleans up the input path by removing leading/trailing slashes and normalizing.

        Args:
            input_path (str): The raw input path.

        Returns:
            str: Sanitized path.
        """
        return input_path.strip("/")

    

    def mkdir(self, dirname):
        """
        Creates a directory at the specified path or current directory.

        Args:
            dirname (str): Directory name or path to create the new directory.

        Raises:
            FileExistsError: If the directory already exists.
        """
        directory_path = f'data/{self.UserID}'
        Groupfile = os.path.join(directory_path,self.Groupfile)
        path = self.path
        # Load the current JSON data
        with open(Groupfile, 'r') as f:
            data = json.load(f)

        # Sanitize and process the path
        dirname = self._sanitize_path(dirname)
        dir_path, new_dir = os.path.split(dirname)
        target_path = self._sanitize_path(dir_path or path)

        # Navigate to the target directory
        current_dir = self._navigate_to_path(data, target_path)

        # Check if the directory already exists
        if "data" not in current_dir:
            current_dir["data"] = {}
        if new_dir in current_dir["data"]:
            return 0

        # Create the new directory
        current_dir["data"][new_dir] = {
            "type": "dir",
            "data": {}
        }

        # Save the updated JSON back to the file
        with open(Groupfile, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Directory '{new_dir}' created successfully at path '{target_path}'.")
        return 1
    
    def cdir(self, new_path):
        """
        Changes the current working directory.

        Args:
            new_path (str): Path to navigate to.

        Raises:
            KeyError: If the path does not exist.
        """
        directory_path = f'data/{self.UserID}'
        Groupfile = os.path.join(directory_path, self.Groupfile)

        if new_path == '..':
        # Go up one directory level (parent directory)
            if self.path:
                # Remove the last directory from the current path
                self.path = '/'.join(self.path.split('/')[:-1])
            print(f"Current directory changed to '{self.path}'.")
            return 1

        if new_path == '/':
            # Go to root directory (empty path)
            self.path = ""
            print(f"Current directory changed to root.")
            return 1
        
        # Load the current JSON data
        with open(Groupfile, 'r') as f:
            data = json.load(f)

        # Sanitize and process the path
        new_path = self._sanitize_path(new_path)

        # If the new path is relative, append it to the current path
        if not new_path.startswith('/'):
            if self.path != "":
                new_path = f"{self.path}/{new_path}"

        # Navigate to verify the path exists from the current path
        if self._navigate_to_path(data, new_path) is None:
            print(f"Invalid path: '{new_path}'")
            return 0

        # Update the current path
        self.path = new_path
        print(f"Current directory changed to '{self.path}'.")
        return 1

    
    def _navigate_to_path(self, data, path):
      """
      Navigate to the specified path in the JSON structure.
      Args:
          data (dict): JSON data.
          path (str): Path string, e.g., "grp1/dipanshu".
      Returns:
          dict: The nested dictionary at the given path.
      Raises:
          KeyError: If the path is invalid.
      """
      current = data
      if path:
          keys = path.split("/")
          for key in keys:
              if key in current["data"]:
                  current = current["data"][key]
              else:
                  return None
      return current

    def add_file(self, filename, file_type, file_id=None, overwrite=False):
        """
        Adds a new file or directory to the JSON structure.

        Args:
            filename (str): Name of the new file or directory.
            file_type (str): Type of the file ('file' or 'dir').
            file_id (str): ID for the file (optional, required if type is 'file').
            overwrite (bool): Whether to overwrite if the file/folder already exists.

        Raises:
            ValueError: If invalid type is provided or if file_id is missing for type 'file'.
            FileExistsError: If a file/folder with the same name exists and overwrite is False.
        """
        directory_path = f'data/{self.UserID}'
        Groupfile = os.path.join(directory_path,self.Groupfile)
        path = self.path

        # Validate the file type
        if file_type not in ["file", "dir"]:
            raise ValueError("Invalid type. Must be 'file' or 'dir'.")

        if file_type == "file" and not file_id:
            raise ValueError("file_id is required for files.")

        # Load the current JSON data
        with open(Groupfile, 'r') as f:
            data = json.load(f)

        # Navigate to the current path
        current_dir = self._navigate_to_path(data, path)

        # Check if the file/folder already exists
        if "data" not in current_dir:
            current_dir["data"] = {}

        if filename in current_dir["data"]:
            if not overwrite:
                return 0
                # raise FileExistsError(f"A file or folder with the name '{filename}' already exists.")
            else:
                print(f"Overwriting existing entry: '{filename}'.")

        # Prepare the new entry
        new_entry = {
            "type": file_type
        }
        if file_type == "file":
            new_entry["fileid"] = file_id
        elif file_type == "dir":
            new_entry["data"] = {}  # Empty directory

        # Add or overwrite the entry
        current_dir["data"][filename] = new_entry

        # Save the updated JSON back to the file
        with open(Groupfile, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"{file_type.capitalize()} '{filename}' added successfully at path '{path}'.")

        return 1
    
    def ls(self,path):
        """
        Lists all files and directories in the current working directory as tuples of (name, type).

        Returns:
            list: A list of tuples, each containing the name and type ('file' or 'dir') of items in the current directory.
        """
        directory_path = f'data/{self.UserID}'
        Groupfile = os.path.join(directory_path, self.Groupfile)

        # Load the current JSON data
        with open(Groupfile, 'r') as f:
            data = json.load(f)

        # Navigate to the current directory
        newpath = self.path + path 
        current_dir = self._navigate_to_path(data,newpath)

        # If the path is invalid or empty
        if current_dir is None:
            print(f"Invalid path: '{self.path}'")
            return []

        # Return a list of tuples (name, type)
        if "data" in current_dir:
            return [(name, item["type"]) for name, item in current_dir["data"].items()]
        else:
            return []
    
    def rm(self, name):
        """
        Removes a file or directory at the specified name in the current path.

        Args:
            name (str): Name of the file or directory to remove.

        Returns:
            int: 1 if the removal is successful, 0 otherwise.
        """
        directory_path = f'data/{self.UserID}'
        Groupfile = os.path.join(directory_path, self.Groupfile)

        # Load the current JSON data
        with open(Groupfile, 'r') as f:
            data = json.load(f)

        # Sanitize the current path and combine with the given name
        target_path = self._sanitize_path(self.path)
        current_dir = self._navigate_to_path(data, target_path)

        if current_dir is None:
            print(f"Invalid current path: '{target_path}'")
            return 0

        # Check if the target name exists
        if "data" not in current_dir or name not in current_dir["data"]:
            print(f"'{name}' does not exist in the current directory.")
            return 0

        # Remove the file or directory
        del current_dir["data"][name]

        # Save the updated JSON back to the file
        with open(Groupfile, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"'{name}' has been removed successfully.")
        return 1


        
