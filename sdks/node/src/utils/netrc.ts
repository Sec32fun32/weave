import {readFileSync, writeFileSync} from 'fs';
import {homedir} from 'os';
import {join} from 'path';

interface NetrcEntry {
  machine: string;
  login: string;
  password: string;
}

export class Netrc {
  private path: string;
  public entries: Map<string, NetrcEntry>;

  constructor(path: string = join(homedir(), '.netrc')) {
    this.path = path;
    this.entries = new Map();
    this.load();
  }

  private load(): void {
    try {
      const content = readFileSync(this.path, 'utf8');
      const lines = content.split('\n');
      let currentMachine: string | null = null;
      let currentEntry: Partial<NetrcEntry> = {};

      for (const line of lines) {
        const [key, value] = line.trim().split(/\s+/);
        switch (key) {
          case 'machine':
            if (currentMachine && Object.keys(currentEntry).length) {
              this.entries.set(currentMachine, currentEntry as NetrcEntry);
            }
            currentMachine = value;
            currentEntry = {machine: value};
            break;
          case 'login':
          case 'password':
        }
      }

      if (currentMachine && Object.keys(currentEntry).length > 1) {
        this.entries.set(currentMachine, currentEntry as NetrcEntry);
      }
    } catch (error) {
      // File doesn't exist or can't be read, starting with empty entries
    }
  }

  save(): void {
    const content = Array.from(this.entries.entries())
      .map(([machine, entry]) => {
        let str = `machine ${machine}\n`;
        if (entry.login) str += `  login ${entry.login}\n`;
        if (entry.password) str += `  password ${entry.password}\n`;
        return str;
      })
      .join('\n');

    writeFileSync(this.path, content, {mode: 0o600});
  }

  getEntry(machine: string): NetrcEntry | undefined {
    return this.entries.get(machine);
  }

  setEntry({machine, ...entryProps}: NetrcEntry): void {
    if (!machine) {
      throw new Error('Machine is required');
    }
    const existing = this.entries.get(machine) ?? {machine};
    const updated = {...existing, ...entryProps, machine};
    this.entries.set(machine, updated);
  }

  getLastEntry(): NetrcEntry | undefined {
    const entries = Array.from(this.entries.values());
    return entries[entries.length - 1];
  }
}
