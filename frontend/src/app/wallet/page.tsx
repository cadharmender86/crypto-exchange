"use client";

import { useState } from "react";
import DepositInrModal from "@/components/wallet/DepositInrModal";

import WalletOverview from "@/components/wallet/WalletOverview";

export default function WalletPage() {
  const [isDepositModalOpen, setIsDepositModalOpen] = useState(false);

  return (
    <>
      <WalletOverview
        onDepositClick={() => setIsDepositModalOpen(true)}
      />
      <DepositInrModal
        open={isDepositModalOpen}
        onClose={() => setIsDepositModalOpen(false)}
      />
    </>
  );
}
