import Sidebar from "./sidebar";

type LayoutProps = {
  children: React.ReactNode;
};

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100 md:flex">
      <Sidebar />

      <main className="flex-1 p-6 md:p-8">
        {children}
      </main>
    </div>
  );
}