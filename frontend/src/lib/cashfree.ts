"use client";

import { load } from "@cashfreepayments/cashfree-js";

export async function getCashfree() {
  const cashfree = await load({
    mode: "sandbox",
  });

  console.log("Cashfree instance:", cashfree);

  return cashfree;
}