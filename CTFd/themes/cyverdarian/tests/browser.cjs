const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  for (const path of [
    "/",
    "/login",
    "/register",
    "/challenges",
    "/scoreboard",
    "/users/2",
    "/users",
    "/rules",
  ]) {
    const response = await page.goto("http://localhost:5080" + path);
    await page.waitForTimeout(700);
    console.log(path, response.status(), await page.title());
    if (response.status() !== 200)
      throw new Error("HTTP " + response.status() + " on " + path);
  }
  for (const width of [1440, 768, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const path of ["/", "/login", "/register"]) {
      await page.goto("http://localhost:5080" + path);
      await page.evaluate(() => document.fonts.ready);
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth))
        throw new Error("guest overflow " + path + " " + width);
      await page.screenshot({
        path: ".data/guest-" + path.replace(/\W+/g, "-") + "-" + width + ".png",
        fullPage: true,
      });
    }
  }
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("http://localhost:5080/login");
  await page.locator("#name").fill("juan_dc");
  await page.locator("#password").fill("preview-password");
  await Promise.all([
    page.waitForURL("**/challenges"),
    page.locator("form input[type=submit]").click(),
  ]);
  await page.locator(".challenge-button").first().waitFor();
  console.log("authenticated cards", await page.locator(".challenge-button").count());
  await page.screenshot({ path: ".data/challenges-desktop.png", fullPage: true });
  await page.getByRole("button", { name: "Web 2", exact: true }).click();
  if ((await page.locator(".challenge-button").count()) !== 2)
    throw new Error("category filter");
  await page.getByRole("searchbox").fill("Union");
  await page.waitForTimeout(250);
  if ((await page.locator(".challenge-button").count()) !== 1)
    throw new Error("search filter");
  await page.getByRole("searchbox").fill("");
  await page.waitForTimeout(250);
  await page.getByRole("button", { name: /Cookie Monster, 100 points/ }).click();
  await page.locator("#challenge-input").waitFor({ state: "visible" });
  console.log("modal available");
  const fileUrl = await page
    .getByRole("link", { name: /cookie_jar.txt/ })
    .getAttribute("href");
  const attachmentResponse = await context.request.get(
    new URL(fileUrl, page.url()).toString(),
  );
  if (
    !attachmentResponse.ok() ||
    !(await attachmentResponse.text()).includes("test attachment")
  )
    throw new Error("attachment download");
  console.log("attachment download OK");
  await page.locator(".challenge-hints summary").first().click();
  await page.screenshot({ path: ".data/challenge-desktop.png", fullPage: true });
  await page.locator("#challenge-input").fill("wrong");
  await page.locator("#challenge-submit").click();
  await page.getByText("Incorrect", { exact: true }).waitFor();
  console.log("incorrect flag response OK");
  await page.locator("#challenge-input").fill("flag{preview_success}");
  await page.locator("#challenge-submit").click();
  await page.getByText("Correct", { exact: true }).waitFor();
  console.log("correct flag response OK");
  await page.keyboard.press("Escape");
  await page.locator("#challenge-window").waitFor({ state: "hidden" });
  if (
    !(await page
      .getByRole("button", { name: /Cookie Monster, 100 points, solved/ })
      .count())
  )
    throw new Error("solved state did not refresh");
  await page.goto("http://localhost:5080/profile");
  await page.locator("#score-graph canvas").waitFor();
  await page.screenshot({ path: ".data/profile-desktop.png", fullPage: true });
  for (const width of [1440, 768, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const path of [
      "/",
      "/challenges",
      "/scoreboard",
      "/profile",
      "/users/2",
      "/notifications",
    ]) {
      const r = await page.goto("http://localhost:5080" + path);
      await page.waitForTimeout(500);
      if (r.status() !== 200) throw new Error(path + " HTTP " + r.status());
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      );
      console.log(width, path, "overflow", overflow);
      if (overflow) throw new Error("horizontal overflow " + width + " " + path);
      if (width === 390 || path === "/scoreboard")
        await page.screenshot({
          path: ".data/" + path.replace(/\W+/g, "-") + "-" + width + ".png",
          fullPage: true,
        });
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("http://localhost:5080/challenges#Cookie%20Monster-1");
  await page.locator("#challenge-input").waitFor({ state: "visible" });
  await page.waitForTimeout(400);
  await page.screenshot({ path: ".data/challenge-mobile.png", fullPage: true });
  await page.waitForTimeout(400);
  await page.keyboard.press("Escape");
  await page.locator("#challenge-window").waitFor({ state: "hidden" });
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await page.getByRole("button", { name: "Account", exact: true }).click();
  await page
    .getByRole("link", { name: "Settings", exact: true })
    .waitFor({ state: "visible" });
  console.log("mobile navigation and challenge deep links OK");
  await page.goto("http://localhost:5080/challenges");
  await page.getByRole("button", { name: /Union Station, 350 points/ }).click();
  await page.locator("#challenge-input").waitFor({ state: "visible" });
  await page.locator("#challenge-input").fill("flag{preview_success}");
  await page.locator("#challenge-submit").click();
  await page.getByText("Correct", { exact: true }).waitFor();
  await page.waitForTimeout(400);
  await page.keyboard.press("Escape");
  await page.locator("#challenge-window").waitFor({ state: "hidden" });
  console.log("dynamic challenge plugin submission OK");
  if (process.argv.includes("--teams")) {
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      for (const path of ["/team", "/teams/1", "/teams"]) {
        const r = await page.goto("http://localhost:5080" + path);
        await page.waitForTimeout(700);
        if (r.status() !== 200)
          throw new Error("team route " + path + " " + r.status());
        if (
          await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)
        )
          throw new Error("team overflow " + path + " " + width);
        await page.screenshot({
          path: ".data/team-" + path.replace(/\W+/g, "-") + "-" + width + ".png",
          fullPage: true,
        });
      }
    }
    await page.goto("http://localhost:5080/team");
    await page.getByRole("button", { name: "Edit team", exact: true }).click();
    await page.locator("#team-edit-modal").waitFor({ state: "visible" });
    await page.waitForTimeout(350);
    await page.locator("#team-edit-modal .btn-close").first().click();
    await page.locator("#team-edit-modal").waitFor({ state: "hidden" });
    console.log("team pages and captain edit modal OK");
  }
  const guest = await browser.newContext();
  const register = await guest.newPage();
  await register.goto("http://localhost:5080/register");
  await register.locator("#name").fill("qa_player");
  await register.locator("#email").fill("qa@example.test");
  await register.locator("#password").fill("preview-password");
  await Promise.all([
    register.waitForURL(url => !url.pathname.includes("register")),
    register.locator("input[type=submit]").click(),
  ]);
  console.log("registration OK");
  await guest.close();
  console.log("BROWSER ERRORS", JSON.stringify(errors));
  if (errors.length) throw new Error("browser errors");
  await browser.close();
})().catch(e => {
  console.error(e);
  process.exit(1);
});
