const { execSync } = require('child_process');
const fs = require('fs');

let outdatedResult = '{}';

// 尝试运行npm outdated命令并获得结果
try {
  outdatedResult = execSync('npm outdated --json', { encoding: 'utf8' });
} catch (error) {
  outdatedResult = error.stdout;  // 使用错误的标准输出作为我们的结果
}

const outdatedPackages = JSON.parse(outdatedResult);

// 读取当前的package.json文件
const packageData = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const packageDataBak = {...packageData}
const { dependencies, devDependencies } = packageData;

// 定义ANSI转义码
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const RESET = '\x1b[0m';

// 更新dependencies中的包版本为最新版本
if (dependencies) {
  for (let pkg in dependencies) {
    if (outdatedPackages[pkg]) {
      console.log(`${RED}Updated package (dependencies): ${pkg} from ${dependencies[pkg]} > ^${outdatedPackages[pkg].latest}${RESET}`);
      dependencies[pkg] = `^${outdatedPackages[pkg].latest}`;
    } else {
      console.log(`${GREEN}Unchanged package (dependencies): ${pkg}${RESET}`);
    }
  }
}

// 更新devDependencies中的包版本为最新版本
if (devDependencies) {
  for (let pkg in devDependencies) {
    if (outdatedPackages[pkg]) {
      console.log(`${RED}Updated package (devDependencies): ${pkg} from ${devDependencies[pkg]} > ^${outdatedPackages[pkg].latest}${RESET}`);
      devDependencies[pkg] = `^${outdatedPackages[pkg].latest}`;
    } else {
      console.log(`${GREEN}Unchanged package (devDependencies): ${pkg}${RESET}`);
    }
  }
}


// 将更新的内容保存为updatePackage.json
fs.writeFileSync('updatePackage.json', JSON.stringify(packageData, null, 2));
fs.writeFileSync('package.bak.json', JSON.stringify(packageDataBak, null, 2));
console.log('Done! Updated versions saved to updatePackage.json');
