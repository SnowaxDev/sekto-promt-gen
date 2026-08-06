import { useState } from "react";
import { Sparkles, Database, Activity as ActivityIcon, Wallet, Leaf } from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui";
import Studio from "./panels/Studio";
import Knowledge from "./panels/Knowledge";
import Usage from "./panels/Usage";
import Activity from "./panels/Activity";

export default function App() {
  const [tab, setTab] = useState("studio");
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-line bg-void/70 backdrop-blur">
        <div className="mx-auto flex max-w-[1400px] items-center gap-3 px-5 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-bright to-forest shadow-glow">
            <Leaf className="h-5 w-5 text-white" />
          </div>
          <div className="leading-tight">
            <div className="text-[15px] font-bold">SeknuTo Forge — Workspace</div>
            <div className="text-xs text-dim">generuj · boduj · uč se · Dark Emerald v3</div>
          </div>
          <div className="ml-auto">
            <Tabs value={tab} onValueChange={setTab}>
              <TabsList>
                <TabsTrigger value="studio"><Sparkles className="h-4 w-4" /> Studio</TabsTrigger>
                <TabsTrigger value="knowledge"><Database className="h-4 w-4" /> Knowledge</TabsTrigger>
                <TabsTrigger value="usage"><Wallet className="h-4 w-4" /> Usage</TabsTrigger>
                <TabsTrigger value="activity"><ActivityIcon className="h-4 w-4" /> Aktivita</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1400px] px-5 py-6">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsContent value="studio"><Studio /></TabsContent>
          <TabsContent value="knowledge"><Knowledge /></TabsContent>
          <TabsContent value="usage"><Usage /></TabsContent>
          <TabsContent value="activity"><Activity /></TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
