import OpenAI from 'openai';
import { op } from '../src/clientApi';

export function createPatchedOpenAI(apiKey: string): OpenAI {
    const openai = new OpenAI({ apiKey });

    const originalCreate = openai.chat.completions.create.bind(openai.chat.completions);
    // @ts-ignore
    openai.chat.completions.create = op(async (...args: Parameters<typeof originalCreate>) => {
        console.log('Patched OpenAI chat.completions.create called');
        return await originalCreate(...args);
    });

    return openai;
}