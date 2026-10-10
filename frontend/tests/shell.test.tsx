import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { SiteShell } from "../src/shared/ui/site-shell";
import { renderToStaticMarkup } from "react-dom/server";
import { shellReferenceHtml } from "../scripts/shell-reference.mjs";

describe("accepted shell", () => {
  it("preserves header/footer links, labels and SVG", () => {
    render(<SiteShell><main id="main-content" /></SiteShell>);
    expect(screen.getByRole("navigation", {name:"Основная навигация"})).toBeTruthy();
    expect(screen.getByRole("navigation", {name:"Навигация в подвале"})).toBeTruthy();
    expect(screen.getAllByRole("link").map(a => [a.textContent, a.getAttribute("href")])).toEqual([
      ["MathStart","/"],["Все темы","/karta-sajta/"],["Личный кабинет","/account/"],
      ["MathStart","/"],["Все темы","/karta-sajta/"],["О проекте","/o-proekte/"],["Контакты","/kontakty/"],
    ]);
    expect(document.querySelector("svg path")?.getAttribute("d")).toBe("M8 17h4l3 6 8-14");
  });
  it("matches canonical Django template elements, attributes and visible text", () => {
    const reference = new DOMParser().parseFromString(shellReferenceHtml(), "text/html");
    const actual = new DOMParser().parseFromString(renderToStaticMarkup(<SiteShell />), "text/html");
    const normalize = (node: Element) => [...node.querySelectorAll("*")].map(el => ({
      tag: el.tagName, attrs: [...el.attributes].map(a => [a.name, a.value]).sort(),
      text: el.children.length ? null : el.textContent?.trim(),
    }));
    for (const selector of [".ms-site-header", ".ms-site-footer"]) {
      expect(normalize(actual.querySelector(selector)!)).toEqual(normalize(reference.querySelector(selector)!));
    }
  });
});
