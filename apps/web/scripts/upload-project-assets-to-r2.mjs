#!/usr/bin/env node

import { createReadStream } from "node:fs";
import { promises as fs } from "node:fs";
import path from "node:path";
import { S3Client, HeadObjectCommand } from "@aws-sdk/client-s3";
import { Upload } from "@aws-sdk/lib-storage";
import {
  collectAssets,
  loadEnvFile,
  REPO_ROOT,
  summarize,
  WEB_ROOT
} from "./project-asset-utils.mjs";

const DEFAULT_MANIFEST = path.join(REPO_ROOT, "r2_asset_manifest.json");

function parseArgs(argv) {
  const args = {
    all: false,
    dryRun: true,
    includeTemporary: false,
    overwrite: false,
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
  console.log(`Upload local auto-video project assets to Cloudflare R2.

Usage:
  npm run r2:plan
  npm run r2:plan -- --project literfy/research-connect-7633832153922489621
  npm run r2:upload -- --all
  npm run r2:upload -- --project projects/figpad/research-connect-google-scholar-template

Required .env.local values:
  R2_ACCOUNT_ID=
  R2_ACCESS_KEY_ID=
  R2_SECRET_ACCESS_KEY=
  R2_BUCKET=auto-video-assets
  R2_PUBLIC_BASE_URL=        optional, only if you set a public/custom domain

Options:
  --all                 Scan every project under ./projects
  --project <path>      Scan one project, for example figpad/research-connect-google-scholar-template
  --dry-run             Only print and write the manifest; do not upload
  --execute             Upload files to Cloudflare R2
  --overwrite           Replace existing R2 objects with the same key
  --include-temporary   Also upload preview_render/render_work segments and QA frames
  --manifest <path>     Output manifest path, default ../../r2_asset_manifest.json
  --prefix <path>       Optional R2 key prefix, for example staging
`);
}

function requiredEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Missing ${name}. Add it to apps/web/.env.local.`);
  return value;
}

function r2Client() {
  const accountId = requiredEnv("R2_ACCOUNT_ID");
  return new S3Client({
    region: "auto",
    endpoint: `https://${accountId}.r2.cloudflarestorage.com`,
    credentials: {
      accessKeyId: requiredEnv("R2_ACCESS_KEY_ID"),
      secretAccessKey: requiredEnv("R2_SECRET_ACCESS_KEY")
    }
  });
}

async function objectExists(client, bucket, key) {
  try {
    await client.send(new HeadObjectCommand({ Bucket: bucket, Key: key }));
    return true;
  } catch (error) {
    const statusCode = error?.$metadata?.httpStatusCode;
    if (statusCode === 404 || error?.name === "NotFound") return false;
    throw error;
  }
}

function publicUrl(key) {
  const baseUrl = process.env.R2_PUBLIC_BASE_URL?.trim().replace(/\/+$/, "");
  if (!baseUrl) return null;
  return `${baseUrl}/${key.split("/").map(encodeURIComponent).join("/")}`;
}

async function uploadAsset(client, bucket, asset, args) {
  if (!args.overwrite && (await objectExists(client, bucket, asset.storage_key))) {
    return {
      ...asset,
      provider: "cloudflare_r2",
      bucket,
      url: publicUrl(asset.storage_key),
      skipped: true,
      skip_reason: "already_exists",
      uploaded_at: null
    };
  }

  const absolutePath = path.join(REPO_ROOT, asset.local_path);
  const upload = new Upload({
    client,
    params: {
      Bucket: bucket,
      Key: asset.storage_key,
      Body: createReadStream(absolutePath),
      ContentType: asset.content_type
    }
  });
  await upload.done();

  return {
    ...asset,
    provider: "cloudflare_r2",
    bucket,
    url: publicUrl(asset.storage_key),
    skipped: false,
    uploaded_at: new Date().toISOString()
  };
}

async function main() {
  await loadEnvFile(path.join(WEB_ROOT, ".env.local"));
  await loadEnvFile(path.join(REPO_ROOT, ".env.local"));

  const args = parseArgs(process.argv.slice(2));
  const assets = await collectAssets(args);
  const uploadedAssets = [];
  let bucket = process.env.R2_BUCKET || "auto-video-assets";
  let client = null;

  if (!args.dryRun) {
    bucket = requiredEnv("R2_BUCKET");
    client = r2Client();
  }

  for (const asset of assets) {
    if (args.dryRun) {
      uploadedAssets.push({ ...asset, provider: "cloudflare_r2", bucket });
      continue;
    }

    console.log(`Uploading ${asset.local_path} -> ${bucket}/${asset.storage_key}`);
    uploadedAssets.push(await uploadAsset(client, bucket, asset, args));
  }

  const manifest = {
    provider: "cloudflare_r2",
    dry_run: args.dryRun,
    bucket,
    include_temporary: args.includeTemporary,
    overwrite: args.overwrite,
    public_base_url: process.env.R2_PUBLIC_BASE_URL || null,
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
