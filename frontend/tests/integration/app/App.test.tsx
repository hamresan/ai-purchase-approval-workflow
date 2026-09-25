import { render, screen } from "@testing-library/react";
import { App } from "../../../src/app/App";

describe("App", () => {
  it("renders the accessible application shell", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Purchase Approval" })).toBeInTheDocument();
  });
});
