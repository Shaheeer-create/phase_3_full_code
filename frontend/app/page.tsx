import { redirect } from "next/navigation";

export default function Home() {
  // Redirect to tasks page (will redirect to login if not authenticated)
  redirect("/tasks");
}
