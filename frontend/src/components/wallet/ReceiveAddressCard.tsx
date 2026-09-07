import { QRCodeSVG } from 'qrcode.react';
import { Copy, CheckCircle } from 'lucide-react';
import { useState } from 'react';

interface Props {
  asset: string;
  network: string;
  address: string;
}

export default function ReceiveAddressCard({
  asset,
  network,
  address,
}: Props) {
  const [copied, setCopied] = useState(false);

  const copyAddress = async () => {
    await navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Receive {asset}</h2>
          <p className="text-sm text-gray-500">{network}</p>
        </div>
      </div>

      <div className="my-6 flex justify-center">
        <QRCodeSVG
          value={address}
          size={220}
          marginSize={2}
        />
      </div>

      <div className="rounded-lg bg-gray-50 p-3 break-all text-sm font-mono">
        {address}
      </div>

      <button
        onClick={copyAddress}
        className="mt-4 w-full rounded-lg bg-blue-600 py-2 text-white hover:bg-blue-700"
      >
        {copied ? (
          <span className="flex items-center justify-center gap-2">
            <CheckCircle size={18} /> Copied
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            <Copy size={18} /> Copy Address
          </span>
        )}
      </button>

      <a
        href={`https://sepolia.etherscan.io/address/${address}`}
        target="_blank"
        rel="noreferrer"
        className="mt-3 block text-center text-sm text-blue-600"
      >
        View on Sepolia Etherscan
      </a>
    </div>
  );
}