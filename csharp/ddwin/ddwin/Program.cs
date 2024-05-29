using ddwin.coreTools;
using System;
using System.Linq;

namespace ddwin
{
    internal static class Program
    {
        private static readonly string[] SupportedCommands = {
            "GetMaxDriver",
            "Path",
        };

        [STAThread]
        public static void Main(string[] args)
        {
            if (args.Length > 0)
            {
                string firstArg = args[0];

                // 忽略大小写比较
                if (SupportedCommands.Contains(firstArg, StringComparer.OrdinalIgnoreCase))
                {
                    if (firstArg.Equals("GetMaxDriver", StringComparison.OrdinalIgnoreCase))
                    {
                        var maxDriver = Resource.GetMaxDriver();
                        Console.WriteLine($"{maxDriver}");
                    }
                    else if (firstArg.Equals("Path", StringComparison.OrdinalIgnoreCase))
                    {
                        if (args.Length >= 2)
                        {
                            PathManager pathManager = new PathManager();
                            string secondArg = args[1];
                            if (new[] { "Add", "Remove", "Is", "Show", "ShowPathType" }.Contains(secondArg, StringComparer.OrdinalIgnoreCase))
                            {
                                if (secondArg.Equals("Add", StringComparison.OrdinalIgnoreCase) && args.Length >= 3)
                                {
                                    string thirdArg = args[2];
                                    thirdArg = Tools.NormalizePath(thirdArg);
                                    pathManager.AddPath(thirdArg);
                                }
                                else if (secondArg.Equals("Remove", StringComparison.OrdinalIgnoreCase) && args.Length >= 3)
                                {
                                    string thirdArg = args[2];
                                    thirdArg = Tools.NormalizePath(thirdArg);
                                    pathManager.RemovePath(thirdArg);
                                }
                                else if (secondArg.Equals("Is", StringComparison.OrdinalIgnoreCase) && args.Length >= 3)
                                {
                                    string thirdArg = args[2];
                                    thirdArg = Tools.NormalizePath(thirdArg);
                                    bool isPath = pathManager.IsPath(thirdArg);
                                    Console.WriteLine(isPath);
                                }
                                else if (secondArg.Equals("Show", StringComparison.OrdinalIgnoreCase))
                                {
                                    string[] paths = pathManager.GetCurrentPath();
                                    foreach (var path in paths)
                                    {
                                        Console.WriteLine(path);
                                    }
                                }
                                else if (secondArg.Equals("ShowPathType", StringComparison.OrdinalIgnoreCase))
                                {
                                    string PathType = pathManager.GetPathType();
                                    Console.WriteLine(PathType);
                                }
                            }
                            else
                            {
                                Console.WriteLine($"Error: Invalid arguments are: Add, Remove, Is, Show, ShowPathType");
                            }
                        }
                        else
                        {
                            Console.WriteLine($"Error: Invalid arguments are: Add, Remove, Is, Show, ShowPathType");
                        }
                    }
                }
                else
                {
                    Console.WriteLine($"Error: Unsupported command '{firstArg}'. Supported commands are: {string.Join(", ", SupportedCommands)}");
                }
            }
            else
            {
                Console.WriteLine($"Error: No command line arguments provided. Supported commands are: {string.Join(", ", SupportedCommands)}");
            }
        }
    }
}
