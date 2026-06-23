import { chromium } from "playwright";
import fs from "node:fs/promises";
import path from "node:path";

const ROOT = "/Users/kk/Desktop/auto video";
const OUT = path.join(ROOT, "figpad_gallery_carousels");
const ASSETS = path.join(OUT, "assets");
const SITE = "https://figpad.ai";
const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

await fs.mkdir(ASSETS, { recursive: true });

function slugify(input) {
  return String(input || "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "figpad-gallery-item";
}

function absoluteUrl(href) {
  return new URL(href, SITE).toString();
}

function imageFromNextUrl(url) {
  const parsed = new URL(url, SITE);
  if (parsed.pathname === "/_next/image" && parsed.searchParams.get("url")) {
    return parsed.searchParams.get("url");
  }
  return parsed.toString();
}

async function download(url, filePath) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Download failed ${response.status}: ${url}`);
  const buffer = Buffer.from(await response.arrayBuffer());
  await fs.writeFile(filePath, buffer);
}

async function screenshotPage(page, url, fileName, viewport = { width: 1440, height: 980 }) {
  await page.setViewportSize(viewport);
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(ASSETS, fileName), fullPage: false });
}

const browser = await chromium.launch({
  headless: true,
  executablePath: chromePath,
});

const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
await page.goto(`${SITE}/scientific-visualization`, { waitUntil: "domcontentloaded", timeout: 60000 });
await page.waitForTimeout(2500);

const categoryLinks = await page.$$eval('a[href^="/scientific-visualization/"]', (anchors) => {
  const seen = new Set();
  return anchors
    .map((a) => ({
      title: a.querySelector("span.block.text-xl")?.textContent?.trim() || a.getAttribute("aria-label") || a.textContent.trim(),
      href: a.getAttribute("href"),
      text: a.textContent.trim(),
    }))
    .filter((item) => item.href && item.href.split("/").length === 3)
    .filter((item) => {
      if (seen.has(item.href)) return false;
      seen.add(item.href);
      return true;
    });
});

const categories = [];
const items = [];
const categorySlugSet = new Set(categoryLinks.map((item) => item.href.split("/").filter(Boolean).at(-1)));

for (const category of categoryLinks) {
  const categoryUrl = absoluteUrl(category.href);
  await page.goto(categoryUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(2500);
  await page.waitForSelector('a[href^="/scientific-visualization/"]', { timeout: 20000 }).catch(() => {});
  const title = await page.locator("h1").first().textContent().catch(() => category.title);
  const cards = await page.$$eval('a[href^="/scientific-visualization/"]', (anchors, categorySlugs) => {
    const categorySlugSet = new Set(categorySlugs);
    const seen = new Set();
    return anchors
      .map((a) => {
        const href = a.getAttribute("href");
        const slug = href?.split("/").filter(Boolean).at(-1) || "";
        const img = a.querySelector("img");
        return {
          href,
          slug,
          title:
            a.querySelector("span.block.text-xl")?.textContent?.trim() ||
            img?.getAttribute("alt")?.replace(/\s+preview$/i, "").replace(/\s+Template$/i, "") ||
            a.textContent.trim(),
          thumb:
            img?.getAttribute("src") ||
            img?.getAttribute("srcset")?.split(",").at(-1)?.trim().split(" ")[0] ||
            "",
        };
      })
      .filter((item) => item.href && item.href.split("/").filter(Boolean).length === 2)
      .filter((item) => item.slug && item.slug !== "scientific-visualization" && !categorySlugSet.has(item.slug))
      .filter((item) => {
        if (seen.has(item.href)) return false;
        seen.add(item.href);
        return true;
      });
  }, [...categorySlugSet]);

  const categorySlug = category.href.split("/").filter(Boolean).at(-1);
  categories.push({
    title: title.trim(),
    slug: categorySlug,
    url: categoryUrl,
    count: cards.length,
  });

  for (const card of cards) {
    items.push({
      category: title.trim(),
      categorySlug,
      title: card.title,
      detailUrl: absoluteUrl(card.href),
      thumbUrl: imageFromNextUrl(card.thumb),
    });
  }
}

const detailPage = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
const detailed = [];
const seenDetail = new Set();

for (const [index, item] of items.entries()) {
  if (seenDetail.has(item.detailUrl)) continue;
  seenDetail.add(item.detailUrl);
  await detailPage.goto(item.detailUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
  await detailPage.waitForTimeout(1500);
  await detailPage.waitForSelector("h1", { timeout: 20000 }).catch(() => {});

  const data = await detailPage.evaluate(() => {
    const meta = (selector) => document.querySelector(selector)?.getAttribute("content") || "";
    const nextImage = document.querySelector('img[src*="cdn.figpad.ai"], img[srcset*="cdn.figpad.ai"]');
    const title = document.querySelector("h1")?.textContent?.trim() || meta('meta[property="og:title"]').replace(/\s+-\s+FigPad$/i, "");
    const prompt = document.querySelector("pre")?.textContent?.trim() || "";
    return {
      title,
      prompt,
      imageUrl: meta('meta[property="og:image"]') || nextImage?.getAttribute("src") || "",
      description: meta('meta[name="description"]') || meta('meta[property="og:description"]') || "",
    };
  });

  const imageUrl = imageFromNextUrl(data.imageUrl || item.thumbUrl);
  const slug = slugify(data.title || item.title);
  const categoryDir = path.join(ASSETS, item.categorySlug);
  await fs.mkdir(categoryDir, { recursive: true });
  const imagePath = path.join(categoryDir, `${String(index + 1).padStart(3, "0")}-${slug}.png`);

  if (imageUrl) {
    await download(imageUrl, imagePath).catch(async () => {
      const fallback = imageUrl.replace("-thumb.webp", ".png");
      await download(fallback, imagePath);
    });
  }

  detailed.push({
    id: `${item.categorySlug}-${String(detailed.length + 1).padStart(3, "0")}`,
    category: item.category,
    categorySlug: item.categorySlug,
    title: data.title || item.title,
    slug,
    detailUrl: item.detailUrl,
    imageUrl,
    imagePath,
    prompt: data.prompt,
    description: data.description,
  });

  console.log(`[${detailed.length}/${items.length}] ${item.categorySlug} / ${data.title || item.title}`);
}

const shots = {
  generateFigure: "site_generate_figure.png",
  svgEditor: "site_svg_editor.png",
  svgConverter: "site_svg_converter.png",
  vectorizer: "site_home_vectorizer.png",
  imageToFigure: "site_home_image_to_figure.png",
};

await screenshotPage(page, `${SITE}/generate-figure`, shots.generateFigure);
await screenshotPage(page, `${SITE}/svg-editor`, shots.svgEditor);
await screenshotPage(page, `${SITE}/svg-converter`, shots.svgConverter);
await screenshotPage(page, `${SITE}/#vectorizer`, shots.vectorizer);
await screenshotPage(page, `${SITE}/#image-to-figure`, shots.imageToFigure);

await download(`${SITE}/logo.png`, path.join(ASSETS, "figpad_logo.png"));

const manifest = {
  scrapedAt: new Date().toISOString(),
  source: `${SITE}/scientific-visualization`,
  categories,
  functionScreenshots: Object.fromEntries(
    Object.entries(shots).map(([key, file]) => [key, path.join(ASSETS, file)])
  ),
  logoPath: path.join(ASSETS, "figpad_logo.png"),
  items: detailed,
};

await fs.writeFile(path.join(OUT, "gallery_manifest.json"), JSON.stringify(manifest, null, 2));
await browser.close();

console.log(`Saved ${detailed.length} gallery items to ${path.join(OUT, "gallery_manifest.json")}`);
