import { authOptions } from "@/constants/authOptions";
import { getServerSession } from "next-auth";
import { signOut } from "next-auth/react";
import { redirect } from "next/navigation";

export default async function SignoutPage() {
  const session = await getServerSession(authOptions);
  const federatedLogout = async () => {
    try {
      const response = await fetch("/api/auth/federated-logout");
      const data = await response.json();
      if (response.ok) {
        await signOut({ redirect: false });
        window.location.href = data.url;
        return;
      }
      throw new Error(data.error);
    } catch (error) {
      console.log(error)
      alert(error);
      await signOut({ redirect: false });
      window.location.href = "/";
    }
  } 
  if (session) {
    return (
      <div className="flex flex-col space-y-3 justify-center items-center h-screen">
        <div className="text-xl font-bold">Signout</div>
        <div>Are you sure you want to sign out?</div>
        <div>
          <button
            onClick={() => federatedLogout()}
            className="bg-sky-500 hover:bg-sky-700 px-5 py-2 text-sm leading-5 rounded-full font-semibold text-white">
            Signout of keycloak
          </button>
        </div>
      </div>
    )
  }
  return redirect("/api/auth/signin")
}
