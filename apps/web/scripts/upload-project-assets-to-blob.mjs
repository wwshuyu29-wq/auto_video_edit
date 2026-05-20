#!/usr/bin/env node

import { createReadStream } from "node:fs";
import { promises as fs } from "node:fs";
import path from "node:path";
import { put } from "@vercel/blob";
import {
  collectAssets,
  loadEnvFile,
  REPO_ROOT,
  summarize,
  WEB_ROOT
} from "./project-asset-utils.mjs";

const DEFAULT_MANIFEST = path.join(REPO_ROOT, "cloud_asset_manifest.json");

function parseArgs(argv) {
  const args = {
    all: false,
    dryRun: true,
    includeTemporary: false,
    overwrite: false,
    publicAccess: true,
    project: null,
    manifest: DEFAULT_MANIFEST,
    prefix: ""
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--all") args.all = true;
    else if (arg === "--execute") args.dryRun = false;
    else if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--include-temporary") args.includeTemporary = true;
    else if (arg === "--overwrite") args.overwrite = true;
    else if (arg === "--private") args.publicAccess = false;
    else if (arg === "--public") args.publicAccess = true;
    else if (arg === "--project") args.project = argv[++index];
    else if (arg === "--manifest") args.manifest = path.resolve(REPO_ROOT, argv[++index]);
    else if (arg === "--prefix") args.prefix = argv[++index].replace(/^\/+|\/+$/g, "");
    else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }

  if (!args.all && !args.project) {
    throw new Error("Choose --all or --project <projects/... path or product/project-id>.");
  }

  return args;
}

function printHelp() {
  console.log(`Upload local auto-video project assets to Vercel Blob.

Usage:
  npm run blob:plan
  npm run blob:plan -- --project literfy/research-connect-7633832153922489621
  npm run blob:upload -- --all
  npm run blob:upload -- --project projects/figpad/research-connect-google-scholar-template

Options:
  --all                 Scan every project under ./projects
  --project <path>      Scan one project, for example figpad/research-connect-google-scholar-template
  --dry-run             Only print and write the manifest; do not upload
  --execute             Upload files to Vercel Blob
  --overwrite           Replace existing Blob objects with the same key
  --include-temporary   Also upload preview_render/render_work segments and QA frames
  --private             Upload with private Blob access instead of public access
  --manifest <path>     Output manifest path, default ../../cloud_asset_manifest.json
  --prefix <path>       Optional Blob key prefix, for example staging
`);
}

async function uploadAsset(asset, args) {
  const absolutePath = path.join(REPO_ROOT, asset.local_path);
  const blob = await put(asset.storage_key, createReadStream(absolutePath), {
    access: args.publicAccess ? "public" : "private",
    addRandomSuffix: false,
    allowOverwrite: args.overwrite,
    contentType: asset.content_type
  });

  return {
    ...asset,
    provider: "vercel_blob",
    url: blob.url,
    download_url: blob.downloadUrl || blob.url,
    uploaded_at: new Date().toISOString()
  };
}

async function main() {
  await loadEnvFile(path.join(WEB_ROOT, ".env.local"));
  await loadEnvFile(path.join(REPO_ROOT, ".env.local"));

  const args = parseArgs(process.argv.slice(2));
  const assets = await collectAssets(args);

  if (!args.dryRun && !process.env.BLOB_READ_WRITE_TOKEN) {
    throw new Error("Missing BLOB_READ_WRITE_TOKEN. Create a Vercel Blob store and run `vercel env pull .env.local --yes` from apps/web.");
  }

  const uploadedAssets = [];
  for (const asset of assets) {
    if (args.dryRun) {
      uploadedAssets.push(asset);
      continue;
    }

    console.log(`Uploading ${asset.local_path} -> ${asset.storage_key}`);
    uploadedAssets.push(await uploadAsset(asset, args));
  }

  const manifest = {
    provider: "vercel_blob",
    dry_run: args.dryRun,
    access: args.publicAccess ? "public" : "private",
    include_temporary: args.includeTemporary,
    overwrite: args.overwrite,
    generated_at: new Date().toISOString(),
    asset_count: uploadedAssets.length,
    summary: summarize(uploadedAssets),
    assets: uploadedAssets
  };

  await fs.writeFile(args.manifest, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(`${args.dryRun ? "Planned" : "Uploaded"} ${uploadedAssets.length} assets.`);
  console.log(`Manifest: ${path.relative(REPO_ROOT, args.manifest)}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
