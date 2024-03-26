const OpenAI = require('openai');

const fs = require('fs');
const crypto = require('crypto');

const client = new OpenAI({
  apiKey: '',
  //sk-7nVZaP1jPhutqnHnDhGmT
  //3BlbkFJoFoK3iAoOiUZp0ES7r87
});


function generatePrompts(fileContent) {
  const data = JSON.parse(fileContent);
  const title = data.title;
  const messages = {};
  const prompts = [];
  const role = 'user'
  let index = 0;
  data.outline.forEach((sectionData, sectionIndex) => {
    const section = sectionData.section;
    sectionData.content.forEach((contentTitle, contentIndex) => {
      const prompt = `你现在是一个论文写作助理，我需要写一篇毕业论文，题目为：《${title}》，请帮我完成 章节 “${section}:${contentTitle}” 的 内容，字数300字，并附上引用文档链接。`;
      const timestamp = Date.now();
      const hash = crypto.createHash('md5').update(`user${timestamp}${sectionIndex}${contentIndex}`).digest('hex');
      const id = `${hash}${timestamp}${sectionIndex}${contentIndex}`;
      prompts.push({ content: prompt, role });
      messages[index]={ id, content: prompt, role,section,contentTitle,title };
      index++
    });
  });
  return { prompts, messages };
}

const filePath = './titles.json';
const fileContent = fs.readFileSync(filePath, 'utf8');
const { prompts, messages } = generatePrompts(fileContent);

let word_len = 0
async function processMessageOne() {
  let index = 0;

  while (prompts.length > 0) {
    const message_one = [prompts.shift()];
    const stream = await client.beta.chat.completions.stream({
      model: 'gpt-3.5-turbo-0613', //gpt-3.5-turbo
      messages: message_one,
      stream: true,
    });

    let message_info = messages[index]
    let {section,contentTitle,title} = message_info
    console.log(`\n论文《${title}》-> ${section} -> ${contentTitle}: \n`)
    stream.on('content', (delta, snapshot) => {
      process.stdout.write(delta);
    });

    let finalContent = '';
    for await (const chunk of stream) {
      finalContent += chunk.choices[0]?.delta?.content || '';
      word_len++
    }

    const chatCompletion = await stream.finalChatCompletion();
    console.log(`chatCompletion`);
    console.log(chatCompletion);
    console.log(`已生成字数: ${word_len}`)
    let con = `\n
${section}:\n
\t${contentTitle}:\n
\t\t${finalContent}\n
    `
    fs.appendFileSync(`chat_output.txt`, con);
    fs.writeFileSync(`chat_output_${index}.txt`, finalContent);
    index++;
  }
}
processMessageOne();



// async function main() {
//   const runner = client.beta.chat.completions
//     .runFunctions({
//       model: 'gpt-3.5-turbo',
//       messages:prompts,
//       functions: [
//         {
//           function: getCurrentLocation,
//           parameters: { type: 'object', properties: {} },
//         },
//         {
//           function: getWeather,
//           parse: JSON.parse,
//           parameters: {
//             type: 'object',
//             properties: {
//               location: { type: 'string' },
//             },
//           },
//         },
//       ],
//     })
//     .on('message', (message) => console.log(message));

//   const finalContent = await runner.finalContent();
//   console.log();
//   console.log('Final content:', finalContent);
// }

// async function getCurrentLocation() {
//   return 'Boston'; // 模拟查找
// }

// async function getWeather(args) {
//   const { location } = args;
//   return { location };
// }

// main();

