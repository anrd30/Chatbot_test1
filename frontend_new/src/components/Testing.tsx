import { useEffect, useMemo, useRef, useState } from 'react';
import { Box, Button, Card, CardContent, CircularProgress, Container, Stack, Typography, FormControlLabel, Switch } from '@mui/material';
import { RedTeamItem, loadRedTeamSet, askBackend } from '../services/testingApi';

export default function Testing() {
  const [items, setItems] = useState<RedTeamItem[]>([]);
  const [idx, setIdx] = useState(0);
  const [answer, setAnswer] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>('');
  type WrongRow = RedTeamItem & { answer: string };
  const [wrong, setWrong] = useState<WrongRow[]>([]);
  const controllerRef = useRef<AbortController | null>(null);
  const timeoutRef = useRef<number | null>(null);
  const [autoAsk, setAutoAsk] = useState<boolean>(false); // off by default

  const current = items[idx];

  useEffect(() => {
    (async () => {
      try {
        const data = await loadRedTeamSet();
        setItems(data);
        setIdx(0);
      } catch (e) {
        setStatus('Failed to load questions');
      }
    })();
    return () => {
      // cleanup on unmount
      if (controllerRef.current) controllerRef.current.abort();
      if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    };
  }, []);

  const hasMore = useMemo(() => idx + 1 < items.length, [idx, items.length]);

  // Optional auto-ask (off by default). When enabled, it behaves like before.
  useEffect(() => {
    if (!autoAsk) return;
    if (!items.length) return;
    const cur = items[idx];
    if (!cur) return;
    if (loading) return;
    if (answer) return; // already answered
    handleAsk();
    return () => {
      if (controllerRef.current) controllerRef.current.abort();
      if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    };
  }, [items, idx, autoAsk]);

  async function handleAsk() {
    if (!current) return;
    setLoading(true);
    setAnswer('');
    setStatus('');
    // abort any previous
    if (controllerRef.current) controllerRef.current.abort();
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    const controller = new AbortController();
    controllerRef.current = controller;
    timeoutRef.current = window.setTimeout(() => {
      controller.abort();
      setStatus('Request timed out after 60s.');
      setLoading(false);
      controllerRef.current = null;
      if (timeoutRef.current) { window.clearTimeout(timeoutRef.current); timeoutRef.current = null; }
      next();
    }, 60_000);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: current.generated_question }),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Backend error ${res.status}`);
      const data = await res.json();
      setAnswer(data.reply);
    } catch (e: any) {
      if (e?.name !== 'AbortError') setStatus(e?.message || 'Failed');
    } finally {
      setLoading(false);
      if (timeoutRef.current) { window.clearTimeout(timeoutRef.current); timeoutRef.current = null; }
      controllerRef.current = null;
    }
  }

  function next() {
    setIdx((i) => Math.min(i + 1, items.length - 1));
    setAnswer('');
    setStatus('');
    // abort timers if any
    if (controllerRef.current) controllerRef.current.abort();
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
  }

  function markWrong() {
    if (current) {
      setWrong((prev) => [
        ...prev,
        {
          ...current,
          answer: answer || '',
        },
      ]);
    }
    next();
  }

  function markCorrect() {
    next();
  }

  function downloadWrong() {
    // Build CSV: category,generated_question,answer,source_question
    const headers = ['category','generated_question','answer','source_question'];
    const rows = wrong.map(w => [
      (w.category || '').replaceAll('"','""'),
      (w.generated_question || '').replaceAll('"','""'),
      (w.answer || '').replaceAll('"','""'),
      (w.source_question || '').replaceAll('"','""'),
    ]);
    const csv = [headers.join(',')]
      .concat(rows.map(r => r.map(v => `"${v}"`).join(',')))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'wrong_questions.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Testing (Red Team)</Typography>
        <Typography variant="body2">Items: {items.length} • Current: {idx + 1}</Typography>

        {current && (
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Category</Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>{current.category}</Typography>

              <Typography variant="subtitle2" color="text.secondary">Source</Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>{current.source_question}</Typography>

              <Typography variant="subtitle2" color="text.secondary">Generated</Typography>
              <Typography variant="h6" sx={{ mb: 2 }}>{current.generated_question}</Typography>

              <Stack direction="row" spacing={1}>
                <Button variant="contained" onClick={handleAsk} disabled={loading}>Ask</Button>
                <Button variant="outlined" color="success" onClick={markCorrect} disabled={loading || !answer}>Correct</Button>
                <Button variant="outlined" color="error" onClick={markWrong} disabled={loading || !answer}>Wrong</Button>
                <Button variant="text" onClick={downloadWrong} disabled={!wrong.length}>Download wrong (CSV)</Button>
                {hasMore && <Button variant="text" onClick={next}>Skip</Button>}
                <FormControlLabel control={<Switch checked={autoAsk} onChange={(e) => setAutoAsk(e.target.checked)} />} label="Auto-ask" />
              </Stack>

              <Box sx={{ mt: 2 }}>
                {loading ? (
                  <Stack direction="row" spacing={1} alignItems="center"><CircularProgress size={20} /><Typography>Waiting for answer…</Typography></Stack>
                ) : answer ? (
                  <>
                    <Typography variant="subtitle2" color="text.secondary">Answer</Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{answer}</Typography>
                  </>
                ) : status ? (
                  <Typography color="error">{status}</Typography>
                ) : null}
              </Box>
            </CardContent>
          </Card>
        )}

        {!current && <Typography>No items loaded.</Typography>}
      </Stack>
    </Container>
  );
}
