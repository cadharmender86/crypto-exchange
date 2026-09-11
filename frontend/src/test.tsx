"use client";

import { useState } from "react";

export default function Test() {
  const [count] = useState(0);

  return <div>{count}</div>;
}