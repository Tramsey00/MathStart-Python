import {it,expect,vi} from "vitest";
import {render,screen,fireEvent} from "@testing-library/react";
import Gallery from "../src/app/routes/foundation-gallery";
it("ports all approved fixture states and four metadata examples",()=>{
  render(<Gallery/>);
  expect(document.querySelectorAll(".ms-ui-grid .ms-ui-state").length).toBe(4);
  expect(document.querySelectorAll(".ms-ui-grid .ms-ui-card").length).toBe(4);
  expect(screen.getByText(/FIXTURE ONLY/)).toBeTruthy();
  expect(document.querySelector("form")).toBeNull();
  expect(document.querySelector("#dispatch-result")?.getAttribute("data-slot")).toBe("self-check");
});
it("preserves raw input through every state, retry and field error without network/storage",()=>{
  const fetch=vi.spyOn(globalThis,"fetch"), storage=vi.spyOn(Storage.prototype,"setItem");
  render(<Gallery/>);
  const input=screen.getByLabelText(/Демонстрационный ввод/) as HTMLInputElement;
  const text="  2 + x \n <script>raw</script> ";
  fireEvent.change(input,{target:{value:text}});
  const raw=input.value; // Native single-line input removes newlines; no further normalization.
  const select=screen.getByLabelText("Демонстрационное состояние");
  for(const state of ["loading","empty","error"])fireEvent.change(select,{target:{value:state}});
  expect(document.querySelector("#demo-alert")?.textContent).toContain("Пример ошибки");
  fireEvent.click(screen.getByRole("button",{name:"Повторить демонстрацию"}));
  expect(document.activeElement).toBe(select);
  expect(document.querySelector("#demo-retry-wrap")?.hasAttribute("hidden")).toBe(true);
  fireEvent.click(screen.getByRole("button",{name:"Показать ошибку поля"}));
  expect(document.activeElement).toBe(input);
  expect(input.getAttribute("aria-invalid")).toBe("true");
  expect(input.value).toBe(raw);
  fireEvent.click(screen.getByRole("button",{name:"Убрать ошибку поля"}));
  expect(input.getAttribute("aria-invalid")).toBe("false");
  expect(input.value).toBe(raw);
  expect(fetch).not.toHaveBeenCalled();expect(storage).not.toHaveBeenCalled();
  fetch.mockRestore();storage.mockRestore();
});
it("selects all slots and controlled unsupported without creating guessed forms",()=>{
  render(<Gallery/>);const select=screen.getByLabelText("Публичный режим");
  for(const [value,slot] of [["0","self-check"],["1","final-answer"],["2","ordered-steps"],["3","structured-solution"],["unsupported","unsupported"]]){
    fireEvent.change(select,{target:{value}});
    expect(document.querySelector("#dispatch-result")?.getAttribute("data-slot")).toBe(slot);
  }
  expect(screen.getByText(/Этот режим или форма schema/)).toBeTruthy();
  expect(document.querySelectorAll("input")).toHaveLength(1);
});
