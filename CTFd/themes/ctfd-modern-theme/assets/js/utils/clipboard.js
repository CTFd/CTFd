import { Tooltip } from "bootstrap";

export function copyToClipboard($input) {
  const tooltip = new Tooltip($input, {
    title: "Copied!",
    trigger: "manual",
  });

  navigator.clipboard.writeText($input.value).then(() => {
    tooltip.show();
    setTimeout(() => {
      tooltip.hide();
    }, 1500);
  });
}
