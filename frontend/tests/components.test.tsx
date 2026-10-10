import { expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button, Card, Field, State } from "../src/shared/ui/components";

it("uses a non-submitting default button and explicit label/error associations", () => {
  render(<><Button>Повторить</Button><Field id="raw" label="Ответ" help="Введите запись" error="Проверьте ввод" /></>);
  expect(screen.getByRole("button").getAttribute("type")).toBe("button");
  const input = screen.getByLabelText("Ответ");
  expect(input.getAttribute("aria-describedby")).toBe("raw-help raw-error");
  expect(input.getAttribute("aria-invalid")).toBe("true");
});

it("escapes untrusted text and exposes loading separately from empty/error", () => {
  render(<><Card title="<script>bad()</script>">{'<img src=x onerror=bad()>'}</Card><State state="loading" title="Загрузка">Ожидание</State></>);
  expect(document.querySelector("script,img")).toBeNull();
  expect(screen.getByText("Загрузка").closest("section")?.getAttribute("aria-busy")).toBe("true");
});
