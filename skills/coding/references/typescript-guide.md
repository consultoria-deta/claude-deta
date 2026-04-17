# TypeScript Guide — Coding Skill Reference

## Types fundamentales

### Primitivos

```typescript
// String
const name: string = 'DETA';
const greeting: string = `Hola, ${name}`;

// Number
const count: number = 42;
const price: number = 99.99;
const percentage: number = 3.14;

// Boolean
const isActive: boolean = true;

// Null y undefined
const value: null = null;
const maybe: string | undefined = undefined;
```

### Arrays y tuples

```typescript
// Array
const names: string[] = ['Juan', 'Ana'];
const counts: Array<number> = [1, 2, 3];

// Tuple (longitud fija, tipos específicos)
const pair: [string, number] = ['edad', 30];
const rgb: [number, number, number] = [255, 128, 0];

// Readonly array
function processItems(items: readonly string[]) {
  // No puede modificar items
}
```

### Objects y interfaces

```typescript
// Interface
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  createdAt: Date;
  metadata?: Record<string, unknown>; // Optional con type adicional
}

// Type alias
type UserRole = 'admin' | 'user' | 'guest';

interface AdminUser extends User {
  permissions: string[];
}

// Implement interface
class UserEntity implements User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  createdAt: Date;

  constructor(data: User) {
    this.id = data.id;
    this.name = data.name;
    this.email = data.email;
    this.role = data.role;
    this.createdAt = data.createdAt;
  }
}
```

### Union types y discriminated unions

```typescript
// Union simple
type Status = 'pending' | 'loading' | 'success' | 'error';

// Union con diferentes formas (discriminated union)
type ApiResponse<T> =
  | { status: 'success'; data: T; timestamp: Date }
  | { status: 'error'; error: string; code: number }
  | { status: 'loading' };

function handleResponse<T>(response: ApiResponse<T>) {
  switch (response.status) {
    case 'success':
      return response.data; // TypeScript sabe que aquí T es el tipo correcto
    case 'error':
      return response.error;
    case 'loading':
      return null;
  }
}
```

### Utility types

```typescript
// Partial — todas las propiedades opcionales
type PartialUser = Partial<User>;

// Required — todas las propiedades requeridas
type RequiredUser = Required<User>;

// Pick — seleccionar propiedades
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit — excluir propiedades
type UserWithoutEmail = Omit<User, 'email'>;

// Record — objeto con keys y values tipados
type UserMap = Record<string, User>;
type RolePermissions = Record<UserRole, string[]>;

// Extract y Exclude
type AdminRole = Extract<UserRole, 'admin' | 'superadmin'>;
type NonAdminRole = Exclude<UserRole, 'admin'>;

// ReturnType
function createUser() {
  return { id: '1', name: 'Juan' };
}
type UserCreated = ReturnType<typeof createUser>;
```

### Generic constraints

```typescript
// Generic con constrain
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: '1', name: 'Juan' };
const name = getProperty(user, 'name'); // string
const id = getProperty(user, 'id'); // string
// getProperty(user, 'invalid') // Error de compilación

// Multiple constraints
function merge<T extends object, U extends object>(target: T, source: U): T & U {
  return { ...target, ...source };
}
```

### Type guards

```typescript
// Type guard con instanceof
function isError(val: unknown): val is Error {
  return val instanceof Error;
}

// Type guard con typeof
function isString(val: unknown): val is string {
  return typeof val === 'string';
}

// Type guard con in
function hasName(val: unknown): val is { name: string } {
  return typeof val === 'string' && 'name' in val;
}

// Exhaustiveness checking
type Shape = Circle | Square | Triangle;

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'square':
      return shape.side ** 2;
    case 'triangle':
      return (shape.base * shape.height) / 2;
    default:
      // Si agregamos un nuevo Shape sin actualizar, esto marca error
      const _exhaustive: never = shape;
      throw new Error(`Unknown shape: ${_exhaustive}`);
  }
}
```

### Mapped types

```typescript
// Hacer todas las propiedades opcionales recursivamente
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

// Hacer todas las propiedades readonly
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

// Renombrar propiedades
type Rename<T, R extends Record<string, string>> = {
  [K in keyof T as K extends keyof R ? R[K] : K]: T[K];
};
```

### Template literal types

```typescript
// Template literals
type Direction = 'top' | 'right' | 'bottom' | 'left';
type Edge = `${Direction}`; // Solo una dirección
type Corners = `${Direction}-${Direction}`; // Combinaciones
type CSSUnit = `${number}${'px' | 'em' | 'rem' | '%'}`;

// Practical example
type EventName = `on${Capitalize<string>}`;
type Handler = { [K in EventName]?: () => void };
```

## Funciones

### Tipado de funciones

```typescript
// Arrow function con tipos explícitos
const add = (a: number, b: number): number => a + b;

// Function declaration
function multiply(a: number, b: number): number {
  return a * b;
}

// Parámetros opcionales
function greet(name: string, greeting?: string): string {
  return greeting ? `${greeting}, ${name}!` : `Hello, ${name}!`;
}

// Default parameters
function createUser(name: string, role: string = 'user'): User {
  return { id: crypto.randomUUID(), name, role, email: '' };
}

// Rest parameters
function sum(...numbers: number[]): number {
  return numbers.reduce((acc, n) => acc + n, 0);
}

// Sobrecarga de funciones
function parseDate(input: string): Date;
function parseDate(input: Date): Date;
function parseDate(input: string | Date): Date {
  if (typeof input === 'string') {
    return new Date(input);
  }
  return input;
}
```

### This types

```typescript
// This en callbacks
function request<T>(
  url: string,
  options: { onSuccess?: (data: T) => void; onError?: (err: Error) => void }
) {
  // ...
  if (options.onSuccess) {
    options.onSuccess(data);
  }
}

// Callable types
interface CallMe {
  (name: string): string;
  description?: string;
}

const callMe: CallMe = (name: string) => `Calling ${name}`;
callMe.description = 'A function that calls someone';
```

## Async y Promises

```typescript
// Promise tipado
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error('User not found');
  }
  return response.json();
}

// Manejo de errores
async function getData(): Promise<Result> {
  try {
    const data = await fetchData();
    return { status: 'success', data };
  } catch (error) {
    if (error instanceof NetworkError) {
      return { status: 'error', message: 'Network failure' };
    }
    return { status: 'error', message: 'Unknown error' };
  }
}

// Promise.all tipado
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
]); // users: User[], posts: Post[]

// Awaited type
type Awaited<T> = T extends Promise<infer U> ? U : T;
```

## Modules

### Import y export

```typescript
// Named exports
export const API_URL = 'https://api.example.com';
export function fetchData() { ... }

// Default export
export default class DataService { ... }

// Import
import { API_URL, fetchData } from './api';
import DataService from './service';
import * as utils from './utils'; // Namespace import

// Type-only imports
import type { User } from './types'; // No se incluye en JS runtime
import { type User, type Admin } from './types'; // Mix
```

### Declaration merging

```typescript
// Extender interfaces
interface Window {
  analytics: Analytics;
}

// Extender modules
declare module '*.svg' {
  const content: string;
  export default content;
}
```
