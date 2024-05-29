using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;

namespace ddwin.coreTools
{
    public class EnvRead
    {
        string annotationSymbol = "#";
        bool initEnv = false;
        string rootDir;
        string envName;
        string delimiter;
        private string localEnvFile;
        string exampleEnvFile;



        public EnvRead(string rootDir = null, string envName = ".env", string delimiter = "=")
        {
            this.rootDir = rootDir ?? Resource.GetDesktopDir();
            this.envName = envName;
            this.delimiter = delimiter;
        }

        public void Init()
        {
            if (!initEnv)
            {
                initEnv = true;
                localEnvFile = GetLocalEnvFile();
                exampleEnvFile = GetExampleEnvFile();
                MergeEnv(new FileInfo(localEnvFile), new FileInfo(exampleEnvFile));
            }
        }


        public string GetLocalEnvFile()
        {
            string localEnvFile = Path.Combine(rootDir, envName);
            if (!File.Exists(localEnvFile))
            {
                File.Create(localEnvFile).Close();
            }
            return localEnvFile;
        }

        public string GetExampleEnvFile()
        {
            string[] exampleFiles = new string[]
            {
            Path.Combine(rootDir, $"{envName}_example"),
            Path.Combine(rootDir, $"{envName}-example"),
            Path.Combine(rootDir, $"{envName}.example")
            };
            foreach (string exampleFile in exampleFiles)
            {
                if (File.Exists(exampleFile))
                {
                    return exampleFile;
                }
            }
            return null;
        }

        public static EnvRead Load(string rootDir, string envName = ".env", string delimiter = "=")
        {
            return new EnvRead(rootDir, envName, delimiter);
        }

        public void MergeEnv(FileInfo envFile, FileInfo exampleEnvFile)
        {
            if (exampleEnvFile == null)
            {
                return;
            }

            var exampleArr = ReadEnv(exampleEnvFile);
            var localArr = ReadEnv(envFile);

            var exampleDict = ArrToDict(exampleArr);
            var localDict = ArrToDict(localArr);

            var addedKeys = exampleDict.Keys.Except(localDict.Keys).ToList();

            foreach (var key in addedKeys)
            {
                localDict[key] = exampleDict[key];
            }

            if (addedKeys.Count > 0)
            {
                Console.WriteLine($"Env-Update env: {envFile.FullName}");
                var updatedArr = DictToArr(localDict);
                SaveEnv(updatedArr, envFile);
                foreach (var addedKey in addedKeys)
                {
                    Console.WriteLine($"Env-Added key: {addedKey}");
                }
            }
        }

        // Assuming ArrToDict, DictToArr, ReadEnv, SaveEnv are defined elsewhere in your class

        public string ReadKey(string key)
        {
            Init();

            using (var reader = new StreamReader(localEnvFile))
            {
                string line;
                while ((line = reader.ReadLine()) != null)
                {
                    char delimiter = '=';
                    var splitLine = line.Trim().Split(new[] { delimiter }, 2);
                    if (splitLine[0].Trim() == key)
                    {
                        return splitLine[1].Trim();
                    }
                }
            }

            return null;
        }

        public void ReplaceOrAddKey(string key, string val)
        {
            var lines = new List<string>();

            using (var reader = new StreamReader(localEnvFile))
            {
                string line;
                while ((line = reader.ReadLine()) != null)
                {
                    char delimiter = '=';
                    var splitLine = line.Trim().Split(new[] { delimiter }, 2);
                    if (splitLine[0].Trim() == key)
                    {
                        lines.Add($"{key}{delimiter}{val}");
                    }
                    else
                    {
                        lines.Add(line.Trim());
                    }
                }
            }

            if (!lines.Any(line => line.StartsWith($"{key}{delimiter}")))
            {
                lines.Add($"{key}{delimiter}{val}");
            }

            using (var writer = new StreamWriter(localEnvFile))
            {
                foreach (var line in lines)
                {
                    writer.WriteLine(line);
                }
            }
        }

        public List<string[]> ReadEnv(FileInfo filePath)
        {
            var result = new List<string[]>();

            using (var reader = new StreamReader(filePath.FullName))
            {
                string content = reader.ReadToEnd().Trim();

                foreach (var line in content.Split('\n'))
                {
                    char delimiter = '=';
                    result.Add(line.Trim().Split(new[] { delimiter }, 2));
                }
            }

            return result;
        }

        public List<string[]> GetEnvs(string filePath = null)
        {
            filePath = filePath ?? localEnvFile;
            var fileInfo = new FileInfo(filePath);
            return ReadEnv(fileInfo);
        }

        public void SaveEnv(List<string[]> envArr, FileInfo filePath)
        {
            using (var writer = new StreamWriter(filePath.FullName))
            {
                foreach (var pair in envArr)
                {
                    writer.WriteLine($"{pair[0]}{delimiter}{pair[1]}");
                }
            }
        }

        public void SetEnv(string key, string value, string filePath = null)
        {
            Init();

            filePath = filePath ?? localEnvFile;
            var fileInfo = new FileInfo(filePath);

            var envArr = ReadEnv(fileInfo);

            bool keyFound = false;

            for (int i = 0; i < envArr.Count; i++)
            {
                if (envArr[i][0] == key)
                {
                    envArr[i] = new string[] { key, value };
                    keyFound = true;
                    break;
                }
            }

            if (!keyFound)
            {
                envArr.Add(new[] { key, value });
            }

            SaveEnv(envArr, fileInfo);
        }

        public bool IsEnv(string key, string filePath = null)
        {
            Init();

            var val = GetEnv(key, filePath);

            bool result = !string.IsNullOrEmpty(val);

            if (Environment.GetCommandLineArgs().Contains("is_env"))
            {
                Console.WriteLine(result ? "True" : "False");
            }

            return result;
        }

        public string GetEnv(string key, string filePath = null)
        {
            Init();

            filePath = filePath ?? localEnvFile;
            var fileInfo = new FileInfo(filePath);

            var envArr = ReadEnv(fileInfo);

            foreach (var pair in envArr)
            {
                if (pair[0] == key)
                {
                    return pair[1];
                }
            }

            return string.Empty;
        }

        public static Dictionary<string, string> ArrToDict(List<string[]> array)
        {
            Dictionary<string, string> dict = new Dictionary<string, string>();

            foreach (var pair in array)
            {
                dict[pair[0]] = pair[1];
            }

            return dict;
        }
        public static List<string[]> DictToArr(Dictionary<string, string> dictionary)
        {
            List<string[]> array = new List<string[]>();

            foreach (var pair in dictionary)
            {
                array.Add(new string[] { pair.Key, pair.Value });
            }

            return array;
        }

        EnvRead env = new EnvRead();
    }


}