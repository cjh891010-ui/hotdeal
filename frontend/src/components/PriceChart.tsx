"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { TrendingDown, Activity } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function PriceChart({ keyword }: { keyword: string }) {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!keyword) return;

        const fetchHistory = async () => {
            setLoading(true);
            try {
                const response = await axios.get(`${API_URL}/deals/price-history/`, {
                    params: { q: keyword }
                });
                setData(response.data);
            } catch (error) {
                console.error("Error fetching price history", error);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [keyword]);

    if (!keyword || data.length < 2) {
        return null; // Don't show chart if not enough data
    }

    const latestPrice = data[data.length - 1].min_price;
    const avgPrice = data.reduce((acc, curr) => acc + curr.avg_price, 0) / data.length;
    const discountRatio = avgPrice > 0 ? ((avgPrice - latestPrice) / avgPrice) * 100 : 0;

    const isGoodDeal = discountRatio > 5; // Consider >5% below average a good deal

    return (
        <Card className="mb-8 overflow-hidden bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
            <CardHeader className="pb-2">
                <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
                    <div>
                        <CardTitle className="text-xl font-bold flex items-center gap-2">
                            <Activity className="h-5 w-5 text-indigo-500" />
                            "{keyword}" 가격 추이
                        </CardTitle>
                        <CardDescription>최근 수집된 핫딜 게시글의 가격 변동 내역입니다.</CardDescription>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className={`px-4 py-2 rounded-lg font-bold text-sm flex items-center gap-2 ${isGoodDeal ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'}`}>
                            신규 최저가: {latestPrice.toLocaleString()}원
                            {isGoodDeal && <TrendingDown className="h-4 w-4" />}
                        </div>
                        {isGoodDeal && (
                            <div className="px-3 py-2 rounded-lg bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 font-bold text-sm">
                                평균 대비 {discountRatio.toFixed(1)}% 저렴!
                            </div>
                        )}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <div className="h-[250px] flex items-center justify-center text-slate-400">
                        데이터를 그리는 중입니다...
                    </div>
                ) : (
                    <div className="h-[300px] w-full mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart
                                data={data}
                                margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                            >
                                <defs>
                                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" className="dark:stroke-slate-800" />
                                <XAxis
                                    dataKey="date"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 12, fill: '#64748b' }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 12, fill: '#64748b' }}
                                    tickFormatter={(value) => `${(value / 10000).toFixed(1)}만`}
                                    dx={-10}
                                />
                                <Tooltip
                                    formatter={(value: any) => [`${value?.toLocaleString?.() || value}원`, '최저가']}
                                    labelFormatter={(label) => `${label} 핫딜 가격`}
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="min_price"
                                    stroke="#6366f1"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorPrice)"
                                    activeDot={{ r: 6, strokeWidth: 0 }}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
