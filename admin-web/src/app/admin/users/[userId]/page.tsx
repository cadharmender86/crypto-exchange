import UserDetails from "@/components/admin/UserDetails";
import UserKycPanel from "@/components/admin/UserKycPanel";

type PageProps = {
  params: Promise<{ userId: string }>;
};

export default async function Page({ params }: PageProps) {
  const { userId } = await params;
  return (
    <div className="space-y-6">
      <UserDetails userId={userId} />
      <div className="mx-auto w-full max-w-7xl">
        <UserKycPanel userId={userId} />
      </div>
    </div>
  );
}
