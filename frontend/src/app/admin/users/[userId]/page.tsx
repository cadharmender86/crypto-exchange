import UserDetails from "@/components/admin/UserDetails";

type PageProps = {
  params: Promise<{ userId: string }>;
};

export default async function Page({ params }: PageProps) {
  const { userId } = await params;
  return <UserDetails userId={userId} />;
}
