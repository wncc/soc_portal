# Frontend Setup and Run

Before running anything, create and fill the `.env` file in the `socfrontend` folder.

You can copy from `.env.example` and then update the values as needed.

To test SSO button locally, change the project id in SSOButton.js and redirect it to localhost instead of production url.

Install pnpm globally:

```bash
npm i -g pnpm
```

Install dependencies:

```bash
pnpm install
```

Build the frontend:

```bash
pnpm build
```

Start the development server:

```bash
pnpm start
```