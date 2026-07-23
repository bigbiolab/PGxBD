import type { NextConfig } from "next";

// Set by the GitHub Pages workflow to "/<repo>" for a project page
// (e.g. https://bigbiolab.github.io/PGxBD/); empty for local dev/build.
const basePath = process.env.NEXT_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath,
};

export default nextConfig;
