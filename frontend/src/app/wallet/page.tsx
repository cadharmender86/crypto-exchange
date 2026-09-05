"use client";

import { useState } from "react";
import DepositInrModal from "@/components/wallet/DepositInrModal";

import WalletOverview from "@/components/wallet/WalletOverview";

export default function WalletPage() {
  const [isDepositModalOpen, setIsDepositModalOpen] = useState(false);
  // const [refreshWallet, setRefreshWallet] = useState(0);

  const handleDepositSuccess = async (): Promise<void> => {
    // Tell WalletOverview to reload wallet balances.
    window.dispatchEvent(new Event("order-created"));
    // Close the modal.
    setIsDepositModalOpen(false);
  };

  return (
    <>
      <WalletOverview
        onDepositClick={() => setIsDepositModalOpen(true)}
        // refreshWallet={refreshWallet}
      />
      <DepositInrModal
        open={isDepositModalOpen}
        onClose={() => setIsDepositModalOpen(false)}
        onPaymentSuccess={handleDepositSuccess}
      />
    </>
  );
}
