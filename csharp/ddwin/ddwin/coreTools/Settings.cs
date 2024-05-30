using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Xml;

namespace ddwin.coreTools
{
    public class Settings : BaseInit
    {
        public string GetSettingsPath()
        {
            string mainPath = Resource.GetMainPath();
            string settingsPath = Path.Combine(mainPath, "settings");
            if (!Directory.Exists(settingsPath))
            {
                Directory.CreateDirectory(settingsPath);
            }
            string settingsFile = Path.Combine(settingsPath, "settings.json");
            if (!File.Exists(settingsFile))
            {
                using (StreamWriter file = File.CreateText(settingsFile))
                {
                    var emptyObject = new { };
                    string jsonString = JsonSerializer.Serialize(emptyObject);
                    file.Write(jsonString);
                }
            }
            return settingsFile;
        }

        public object Get(string key)
        {
            string settingsFile = GetSettingsPath();
            using (StreamReader file = File.OpenText(settingsFile))
            {
                var settings = JsonSerializer.Deserialize<Dictionary<string, object>>(file.ReadToEnd());
                if (settings.ContainsKey(key))
                {
                    return settings[key];
                }
            }
            return null;
        }

        public void Set(string key, object value)
        {
            string settingsFile = GetSettingsPath();
            Dictionary<string, object> settings;
            using (StreamReader file = File.OpenText(settingsFile))
            {
                settings = JsonSerializer.Deserialize<Dictionary<string, object>>(file.ReadToEnd());
            }
            settings[key] = value;
            using (StreamWriter file = File.CreateText(settingsFile))
            {
                string jsonString = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
                file.Write(jsonString);
            }
        }

        public Dictionary<string, object> GetAll()
        {
            string settingsFile = GetSettingsPath();
            using (StreamReader file = File.OpenText(settingsFile))
            {
                return JsonSerializer.Deserialize<Dictionary<string, object>>(file.ReadToEnd());
            }
        }

        public void SetIni(string filename, string val = "", string key = "default")
        {
            if (!filename.EndsWith(".ini"))
            {
                filename += ".ini";
            }

            string settingsDir = Path.Combine(Resource.GetMainPath(), ".info", filename);

            if (!File.Exists(settingsDir))
            {
                File.Create(settingsDir).Close();
            }

            Dictionary<string, string> settings = new Dictionary<string, string>();

            foreach (string line in File.ReadLines(settingsDir))
            {
                if (line.Contains('='))
                {
                    string[] parts = line.Split(new char[] { '=' }, 2);
                    settings[parts[0].Trim()] = parts[1].Trim();
                }
            }

            settings[key] = val;

            using (StreamWriter file = new StreamWriter(settingsDir))
            {
                foreach (KeyValuePair<string, string> entry in settings)
                {
                    file.WriteLine($"{entry.Key}={entry.Value}");
                }
            }

            Console.WriteLine($"Key '{key}' set to '{val}' in file '{filename}' successfully.");
        }

        public string GetIni(string filename, string key = "default")
        {
            if (!filename.EndsWith(".ini"))
            {
                filename += ".ini";
            }

            string settingsDir = Path.Combine(Resource.GetMainPath(), ".info", filename);

            if (!File.Exists(settingsDir))
            {
                Console.WriteLine($"File '{filename}' does not exist.");
                return "";
            }

            Dictionary<string, string> settings = new Dictionary<string, string>();

            foreach (string line in File.ReadLines(settingsDir))
            {
                if (line.Contains('='))
                {
                    string[] parts = line.Split(new char[] { '=' }, 2);
                    settings[parts[0].Trim()] = parts[1].Trim();
                }
            }

            string value;
            if (settings.TryGetValue(key, out value))
            {
                return value;
            }
            else
            {
                return "";
            }
        }

        Settings settings = new Settings();

    }
}
