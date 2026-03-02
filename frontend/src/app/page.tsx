"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Search, Flame, TrendingDown, Bell, MessageSquare, ThumbsUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";
import { PriceChart } from "@/components/PriceChart";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Deal {
  id: number;
  title: string;
  price: number;
  shipping_fee: number;
  mall: string;
  source: string;
  url: string;
  created_at: string;
  likes: number;
  comments: number;
  is_ended: boolean;
}

const getSourceColor = (source: string) => {
  switch (source) {
    case "fmkorea": return "bg-blue-500";
    case "algumon": return "bg-red-500";
    case "momibebe": return "bg-pink-500";
    default: return "bg-slate-500";
  }
};

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("latest");
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);

  // Alert Modal state
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [alertEmail, setAlertEmail] = useState("");
  const [alertKeyword, setAlertKeyword] = useState("");
  const [alertStatus, setAlertStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alertEmail || !alertKeyword) return;

    setAlertStatus("loading");
    try {
      await axios.post(`${API_URL}/alerts/`, {
        email: alertEmail,
        keyword: alertKeyword,
      });
      setAlertStatus("success");
      setTimeout(() => {
        setIsAlertModalOpen(false);
        setAlertStatus("idle");
        setAlertKeyword("");
      }, 1500);
    } catch (error) {
      console.error("Error creating alert:", error);
      setAlertStatus("error");
    }
  };

  useEffect(() => {
    const fetchDeals = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/deals/`, {
          params: {
            q: searchQuery || undefined,
            sort: activeTab,
          }
        });
        setDeals(response.data);
      } catch (error) {
        console.error("Error fetching deals:", error);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(fetchDeals, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery, activeTab]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
      <header className="sticky top-0 z-50 w-full border-b bg-white/80 dark:bg-slate-950/80 backdrop-blur">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingDown className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            <span className="font-bold text-xl tracking-tight">DealFlow</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => setIsAlertModalOpen(true)}>
              <Bell className="h-5 w-5" />
            </Button>
            <Button className="hidden sm:flex rounded-full bg-indigo-600 hover:bg-indigo-700 text-white">
              로그인
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <section className="py-12 md:py-20 flex flex-col items-center text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight">
              모든 핫딜을 <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-cyan-500">한 곳에서</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              에펨코리아, 알구몬, 맘이베베의 최저가를 실시간으로 비교하고 똑똑하게 구매하세요.
            </p>
          </div>

          <div className="w-full max-w-2xl relative group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
            </div>
            <Input
              type="text"
              placeholder="찾고 있는 상품을 검색해보세요 (예: 크리넥스, 제로콜라)"
              className="w-full h-14 pl-12 pr-4 rounded-full border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-lg shadow-sm focus-visible:ring-indigo-500 transition-shadow hover:shadow-md"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </section>

        {searchQuery && deals.length > 0 && (
          <PriceChart keyword={searchQuery} />
        )}

        {deals.length > 0 && !searchQuery && (
          <section className="mb-12">
            <div className="flex items-center gap-2 mb-6">
              <Flame className="h-5 w-5 text-red-500" />
              <h2 className="text-2xl font-bold">실시간 핫딜 TOP 5</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {deals.slice(0, 5).map((deal) => (
                <Card key={`top-${deal.id}`} className="overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800">
                  <CardContent className="p-4 flex flex-col h-full justify-between gap-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-start">
                        <Badge className={`${getSourceColor(deal.source)} text-white border-0 font-medium`}>
                          {deal.source === "fmkorea" ? "에펨코리아" : deal.source === "algumon" ? "알구몬" : deal.source}
                        </Badge>
                        <span className="text-xs font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md">
                          {deal.mall || "외부몰"}
                        </span>
                      </div>
                      <h3 className="font-semibold text-sm leading-tight line-clamp-2">
                        {deal.title}
                      </h3>
                      {(deal.likes > 0 || deal.comments > 0) && (
                        <div className="flex gap-3 text-xs font-medium text-slate-500">
                          {deal.likes > 0 && <span className="flex items-center gap-1 text-red-500"><ThumbsUp className="h-3 w-3 inline" /> {deal.likes}</span>}
                          {deal.comments > 0 && <span className="flex items-center gap-1 text-blue-500"><MessageSquare className="h-3 w-3 inline" /> {deal.comments}</span>}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                        {deal.price > 0 ? `${deal.price.toLocaleString()}원` : "가격 미상"}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        )}

        <section>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <h2 className="text-2xl font-bold">{searchQuery ? '검색 결과' : '맞춤형 피드'}</h2>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-[300px]">
              <TabsList className="grid w-full grid-cols-2 bg-slate-100 dark:bg-slate-800 rounded-full p-1">
                <TabsTrigger value="latest" className="rounded-full rounded-r-md">최신순</TabsTrigger>
                <TabsTrigger value="price" className="rounded-full rounded-l-md">가격순</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-12 text-slate-500">데이터를 불러오는 중입니다...</div>
            ) : deals.length === 0 ? (
              <div className="text-center py-12 text-slate-500">조건에 맞는 핫딜이 없습니다.</div>
            ) : (
              deals.map((deal) => (
                <Card key={deal.id} className="flex flex-col sm:flex-row overflow-hidden hover:border-indigo-200 transition-colors bg-white dark:bg-slate-900 relative">
                  <div className={`sm:w-2 absolute left-0 top-0 bottom-0 ${getSourceColor(deal.source)}`}></div>
                  <CardContent className="p-5 pl-7 flex flex-col justify-between w-full">
                    <div>
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <Badge variant="outline" className="text-xs text-slate-600">
                          {deal.source === "fmkorea" ? "에펨코리아" : deal.source === "algumon" ? "알구몬" : deal.source}
                        </Badge>
                        <span className="text-xs text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 rounded-md">
                          {deal.mall || "외부몰"}
                        </span>
                        <span className="text-xs text-slate-400">
                          {formatDistanceToNow(new Date(deal.created_at + "Z"), { addSuffix: true, locale: ko })}
                        </span>
                        {(deal.likes > 0 || deal.comments > 0) && (
                          <div className="flex items-center gap-3 ml-2 text-xs font-medium text-slate-500">
                            {deal.likes > 0 && <span className="flex items-center gap-1 text-red-500"><ThumbsUp className="h-3 w-3 inline" /> {deal.likes}</span>}
                            {deal.comments > 0 && <span className="flex items-center gap-1 text-blue-500"><MessageSquare className="h-3 w-3 inline" /> {deal.comments}</span>}
                          </div>
                        )}
                      </div>
                      <a href={deal.url} target="_blank" rel="noopener noreferrer">
                        <h3 className="font-bold text-lg cursor-pointer hover:text-indigo-600 transition-colors line-clamp-2">
                          {deal.title}
                        </h3>
                      </a>
                    </div>
                    <div className="flex items-center justify-between mt-4">
                      <span className="text-xl font-bold">
                        {deal.price > 0 ? `${deal.price.toLocaleString()}원` : "무료 / 가격 미상"}
                      </span>
                      <a href={deal.url} target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" size="sm" className="rounded-full">
                          상세보기
                        </Button>
                      </a>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </section>
      </main>

      <Dialog open={isAlertModalOpen} onOpenChange={setIsAlertModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>키워드 알림 등록</DialogTitle>
            <DialogDescription>
              원하시는 상품의 키워드와 이메일을 등록하시면, 새로운 핫딜이 떴을 때 알려드립니다.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateAlert}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="email" className="text-right">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  className="col-span-3"
                  value={alertEmail}
                  onChange={(e) => setAlertEmail(e.target.value)}
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="keyword" className="text-right">키워드</Label>
                <Input
                  id="keyword"
                  placeholder="예: 크리넥스, 제로콜라"
                  className="col-span-3"
                  value={alertKeyword}
                  onChange={(e) => setAlertKeyword(e.target.value)}
                  required
                />
              </div>
            </div>

            {alertStatus === "success" && (
              <p className="text-sm text-green-600 text-center mb-4">알림이 성공적으로 등록되었습니다!</p>
            )}
            {alertStatus === "error" && (
              <p className="text-sm text-red-600 text-center mb-4">등록 중 오류가 발생했습니다. 다시 시도해주세요.</p>
            )}

            <DialogFooter>
              <Button type="submit" disabled={alertStatus === "loading" || alertStatus === "success"} className="bg-indigo-600 hover:bg-indigo-700">
                {alertStatus === "loading" ? "등록 중..." : "알림 받기"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
