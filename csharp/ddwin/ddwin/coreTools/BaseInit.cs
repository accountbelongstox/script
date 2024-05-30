using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ddwin.coreTools
{
    public class BaseInit
    {
        public const int StdOutputHandle = -11;
        public const ConsoleColor ForegroundRed = ConsoleColor.Red;
        public const ConsoleColor ForegroundGreen = ConsoleColor.Green;
        public const ConsoleColor ForegroundYellow = ConsoleColor.Yellow;

        public void SetRestart(bool isRestart = false)
        {
            string restartFile = Resource.GetMainInfoPath(".restart.ini"); // Assuming GetMainInfoPath is a method that returns the path

            if (isRestart)
            {
                using (StreamWriter sw = File.CreateText(restartFile))
                {
                    sw.WriteLine("Restart enabled");
                }
            }
            else
            {
                if (File.Exists(restartFile))
                {
                    File.Delete(restartFile);
                }
            }
        }

        public bool CheckAdmin()
        {
            try
            {
                using (StreamWriter writer = new StreamWriter("C:\\Windows\\System32\\config\\systemTest"))
                {
                    writer.Write("Test");
                }
                return true;
            }
            catch (UnauthorizedAccessException)
            {
                return false;
            }
        }

        public string ReadFile(string fileName, string encoding = "utf-8", bool info = false)
        {
            List<string> codings = new List<string>
    {
            "utf-8",
            "utf-16",
            "utf-16le",
            "utf-16BE",
            "gbk",
            "gb2312",
            "us-ascii",
            "ascii",
            "IBM037",
            "IBM437",
            "IBM500",
            "ASMO-708",
            "DOS-720",
            "ibm737",
            "ibm775",
            "ibm850",
            "ibm852",
            "IBM855",
            "ibm857",
            "IBM00858",
            "IBM860",
            "ibm861",
            "DOS-862",
            "IBM863",
            "IBM864",
            "IBM865",
            "cp866",
            "ibm869",
            "IBM870",
            "windows-874",
            "cp875",
            "shift_jis",
            "ks_c_5601-1987",
            "big5",
            "IBM1026",
            "IBM01047",
            "IBM01140",
            "IBM01141",
            "IBM01142",
            "IBM01143",
            "IBM01144",
            "IBM01145",
            "IBM01146",
            "IBM01147",
            "IBM01148",
            "IBM01149",
            "windows-1250",
            "windows-1251",
            "Windows-1252",
            "windows-1253",
            "windows-1254",
            "windows-1255",
            "windows-1256",
            "windows-1257",
            "windows-1258",
            "Johab",
            "macintosh",
            "x-mac-japanese",
            "x-mac-chinesetrad",
            "x-mac-korean",
            "x-mac-arabic",
            "x-mac-hebrew",
            "x-mac-greek",
            "x-mac-cyrillic",
            "x-mac-chinesesimp",
            "x-mac-romanian",
            "x-mac-ukrainian",
            "x-mac-thai",
            "x-mac-ce",
            "x-mac-icelandic",
            "x-mac-turkish",
            "x-mac-croatian",
            "utf-32",
            "utf-32BE",
            "x-Chinese-CNS",
            "x-cp20001",
            "x-Chinese-Eten",
            "x-cp20003",
            "x-cp20004",
            "x-cp20005",
            "x-IA5",
            "x-IA5-German",
            "x-IA5-Swedish",
            "x-IA5-Norwegian",
            "x-cp20261",
            "x-cp20269",
            "IBM273",
            "IBM277",
            "IBM278",
            "IBM280",
            "IBM284",
            "IBM285",
            "IBM290",
            "IBM297",
            "IBM420",
            "IBM423",
            "IBM424",
            "x-EBCDIC-KoreanExtended",
            "IBM-Thai",
            "koi8-r",
            "IBM871",
            "IBM880",
            "IBM905",
            "IBM00924",
            "EUC-JP",
            "x-cp20936",
            "x-cp20949",
            "cp1025",
            "koi8-u",
            "iso-8859-1",
            "iso-8859-2",
            "iso-8859-3",
            "iso-8859-4",
            "iso-8859-5",
            "iso-8859-6",
            "iso-8859-7",
            "iso-8859-8",
            "iso-8859-9",
            "iso-8859-13",
            "iso-8859-15",
            "x-Europa",
            "iso-8859-8-i",
            "iso-2022-jp",
            "csISO2022JP",
            "iso-2022-jp",
            "iso-2022-kr",
            "x-cp50227",
            "euc-jp",
            "EUC-CN",
            "euc-kr",
            "hz-gb-2312",
            "GB18030",
            "x-iscii-de",
            "x-iscii-be",
            "x-iscii-ta",
            "x-iscii-te",
            "x-iscii-as",
            "x-iscii-or",
            "x-iscii-ka",
            "x-iscii-ma",
            "x-iscii-gu",
            "x-iscii-pa",
            "utf-7",
            };

            if (encoding != null)
            {
                codings.Insert(0, encoding);
            }

            foreach (string coding in codings)
            {
                try
                {
                    using (StreamReader sr = new StreamReader(fileName, Encoding.GetEncoding(coding)))
                    {
                        string content = sr.ReadToEnd();

                        if (info)
                        {
                            Console.WriteLine($"Successfully read {fileName} with encoding {coding}");
                        }

                        return content;
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine($"File open error: {fileName}");
                    Console.WriteLine(e);
                }
            }

            return "";
        }

        public void SaveFile(string fileName, string content = "", string mode = "w", string encoding = "utf-8")
        {
            Console.WriteLine($"Saving file '{fileName}'...");
            string baseDir = Path.GetDirectoryName(fileName);
            if (!Directory.Exists(baseDir))
            {
                Directory.CreateDirectory(baseDir);
            }
            using (StreamWriter file = new StreamWriter(fileName, mode == "w", Encoding.GetEncoding(encoding)))
            {
                file.Write(content);
            }
            Console.WriteLine($"File '{fileName}' saved successfully.");
        }


        public (string, string, int) ExecuteCommand(string command, string input = null)
        {
            Console.WriteLine($"Executing command: {command}");

            var startInfo = new ProcessStartInfo
            {
                FileName = "/bin/bash",
                ArgumentList = { "-c", command },
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };

            using var process = new Process { StartInfo = startInfo };
            process.Start();

            if (!string.IsNullOrEmpty(input))
            {
                process.StandardInput.Write(input);
            }

            string stdOutput = process.StandardOutput.ReadToEnd();
            string stdError = process.StandardError.ReadToEnd();

            process.WaitForExit();

            int returnCode = process.ExitCode;

            if (returnCode != 0)
            {
                Console.WriteLine($"Command: '{command}' code {returnCode}");
                Console.WriteLine("STDOUT:");
                Console.WriteLine(stdOutput);
                Console.WriteLine("STDERR:");
                Console.WriteLine(stdError);
            }
            else
            {
                Console.WriteLine(stdOutput.Trim());
            }

            return (stdOutput, stdError, returnCode);
        }


    }
}
