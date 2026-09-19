"use client";

import { useEffect, useMemo, useState } from "react";

type TopPrediction = {
  disease: string;
  model_score: number;
};

type PredictionResult = {
  predicted_disease: string;
  model_score: number;

  confidence_level: string;
  confidence_warning: boolean;
  confidence_warning_message: string | null;

  top_predictions: TopPrediction[];

  recognized_symptoms: string[];
  unrecognized_symptoms: string[];

  symptom_warning: boolean;
  symptom_warning_message: string | null;

  emergency_warning: boolean;
  emergency_warning_message: string | null;
  emergency_symptoms: string[];

  description: string;
  medications: string[];
  precautions: string[];
  diet: string[];
  workout: string[];
};

type SymptomsResponse = {
  symptoms: string[];
};

export default function Home() {
  const [availableSymptoms, setAvailableSymptoms] = useState<string[]>(
    []
  );

  const [symptomsLoading, setSymptomsLoading] = useState(true);
  const [symptomsError, setSymptomsError] = useState("");

  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [customSymptom, setCustomSymptom] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD SYMPTOMS
  // ============================================================

  useEffect(() => {
    const loadSymptoms = async () => {
      try {
        setSymptomsLoading(true);
        setSymptomsError("");

        const response = await fetch(
          "http://127.0.0.1:8000/symptoms"
        );

        if (!response.ok) {
          throw new Error(
            "Unable to load symptoms from the backend."
          );
        }

        const data: SymptomsResponse = await response.json();

        setAvailableSymptoms(data.symptoms || []);
      } catch (err) {
        if (err instanceof Error) {
          setSymptomsError(err.message);
        } else {
          setSymptomsError(
            "Unable to load the available symptoms."
          );
        }
      } finally {
        setSymptomsLoading(false);
      }
    };

    loadSymptoms();
  }, []);

  // ============================================================
  // FILTER SYMPTOMS
  // ============================================================

  const filteredSymptoms = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();

    if (!search) {
      return availableSymptoms.filter(
        (symptom) => !selectedSymptoms.includes(symptom)
      );
    }

    return availableSymptoms.filter((symptom) => {
      const matchesSearch = symptom
        .toLowerCase()
        .includes(search);

      const alreadySelected =
        selectedSymptoms.includes(symptom);

      return matchesSearch && !alreadySelected;
    });
  }, [
    availableSymptoms,
    selectedSymptoms,
    searchTerm,
  ]);

  // ============================================================
  // NAVIGATION
  // ============================================================

  const scrollToSection = (sectionId: string) => {
    const section = document.getElementById(sectionId);

    if (section) {
      section.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  // ============================================================
  // SELECT / REMOVE SYMPTOM
  // ============================================================

  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms((current) => {
      const exists = current.some(
        (item) =>
          item.toLowerCase() === symptom.toLowerCase()
      );

      if (exists) {
        return current.filter(
          (item) =>
            item.toLowerCase() !== symptom.toLowerCase()
        );
      }

      return [...current, symptom];
    });

    setResult(null);
    setError("");
  };

  // ============================================================
  // ADD CUSTOM SYMPTOM
  // ============================================================

  const addCustomSymptom = () => {
    const symptom = customSymptom.trim();

    if (!symptom) {
      return;
    }

    const alreadySelected = selectedSymptoms.some(
      (item) =>
        item.toLowerCase() === symptom.toLowerCase()
    );

    if (!alreadySelected) {
      setSelectedSymptoms((current) => [
        ...current,
        symptom,
      ]);
    }

    setCustomSymptom("");
    setSearchTerm("");
    setResult(null);
    setError("");
  };

  // ============================================================
  // CUSTOM INPUT ENTER
  // ============================================================

  const handleCustomSymptomKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addCustomSymptom();
    }
  };

  // ============================================================
  // ANALYZE SYMPTOMS
  // ============================================================

  const analyzeSymptoms = async () => {
    if (
      selectedSymptoms.length === 0 ||
      loading
    ) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/predict",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            symptoms: selectedSymptoms,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to analyze symptoms."
        );
      }

      setResult(data);

      setTimeout(() => {
        const resultSection =
          document.getElementById("results");

        if (resultSection) {
          resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      }, 100);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to connect to the AI HealthMate backend."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // START NEW ANALYSIS
  // ============================================================

  const startNewAnalysis = () => {
    setSelectedSymptoms([]);
    setCustomSymptom("");
    setSearchTerm("");
    setResult(null);
    setError("");

    scrollToSection("home");
  };

  // ============================================================
  // CONFIDENCE STYLE
  // ============================================================

  const getConfidenceStyle = () => {
    if (!result) {
      return {
        badge: "bg-slate-100 text-slate-700",
        bar: "bg-slate-500",
      };
    }

    if (
      result.confidence_level.toLowerCase() === "high"
    ) {
      return {
        badge: "bg-green-100 text-green-700",
        bar: "bg-green-500",
      };
    }

    if (
      result.confidence_level.toLowerCase() ===
      "moderate"
    ) {
      return {
        badge: "bg-yellow-100 text-yellow-700",
        bar: "bg-yellow-500",
      };
    }

    return {
      badge: "bg-red-100 text-red-700",
      bar: "bg-red-500",
    };
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">

        <div className="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 py-3 sm:px-6 sm:py-4">

          {/* Logo */}

          <button
            type="button"
            onClick={() => scrollToSection("home")}
            className="text-left"
          >

            <h1 className="text-lg font-bold tracking-tight text-teal-700 sm:text-2xl">
              AI HealthMate
            </h1>

            <p className="hidden text-xs text-slate-500 sm:block">
              AI-powered health decision support
            </p>

          </button>

          {/* Desktop Navigation */}

          <nav className="hidden items-center gap-2 sm:flex">

            <button
              type="button"
              onClick={() => scrollToSection("home")}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-teal-50 hover:text-teal-700"
            >
              Home
            </button>

            <button
              type="button"
              onClick={() => scrollToSection("how-it-works")}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-teal-50 hover:text-teal-700"
            >
              How It Works
            </button>

            <button
              type="button"
              onClick={() => scrollToSection("about")}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-teal-50 hover:text-teal-700"
            >
              About
            </button>

          </nav>

          {/* Mobile navigation */}

          <div className="flex min-w-0 items-center gap-0.5 sm:hidden">

            <button
              type="button"
              onClick={() => scrollToSection("home")}
              className="whitespace-nowrap rounded-lg px-2 py-2 text-[11px] font-medium text-slate-600 hover:bg-teal-50 hover:text-teal-700"
            >
              Home
            </button>

            <button
              type="button"
              onClick={() => scrollToSection("how-it-works")}
              className="whitespace-nowrap rounded-lg px-2 py-2 text-[11px] font-medium text-slate-600 hover:bg-teal-50 hover:text-teal-700"
            >
              How It Works
            </button>

            <button
              type="button"
              onClick={() => scrollToSection("about")}
              className="whitespace-nowrap rounded-lg px-2 py-2 text-[11px] font-medium text-slate-600 hover:bg-teal-50 hover:text-teal-700"
            >
              About
            </button>

          </div>

        </div>

      </header>

      {/* ================================================== */}
      {/* HOME / HERO */}
      {/* ================================================== */}

      <section
        id="home"
        className="scroll-mt-24 bg-gradient-to-b from-teal-50 via-white to-slate-50"
      >

        <div className="mx-auto max-w-6xl px-4 py-12 text-center sm:px-6 sm:py-20">

          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-100 text-2xl shadow-sm sm:mb-6 sm:h-16 sm:w-16 sm:text-3xl">
            🩺
          </div>

          <h2 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">

            Understand your symptoms with{" "}

            <span className="text-teal-700">
              AI HealthMate
            </span>

          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">

            Enter your symptoms and let our machine learning
            system provide a possible disease prediction along
            with helpful health information and recommendations.

          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">

            <span className="rounded-full bg-white px-4 py-2 text-slate-600 shadow-sm ring-1 ring-slate-200">
              🤖 AI Prediction
            </span>

            <span className="rounded-full bg-white px-4 py-2 text-slate-600 shadow-sm ring-1 ring-slate-200">
              📊 Top Predictions
            </span>

            <span className="rounded-full bg-white px-4 py-2 text-slate-600 shadow-sm ring-1 ring-slate-200">
              💡 Health Recommendations
            </span>

          </div>

        </div>

      </section>

      {/* ================================================== */}
      {/* SYMPTOM INPUT */}
      {/* ================================================== */}

      <section
        id="symptoms"
        className="scroll-mt-24 mx-auto max-w-5xl px-6 py-12"
      >

        <div className="rounded-3xl bg-white p-4 shadow-sm ring-1 ring-slate-200 sm:p-10">

          <div className="mb-8">

            <div className="flex items-center gap-3">

              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 text-sm font-bold text-teal-700">
                1
              </span>

              <p className="text-sm font-semibold uppercase tracking-wider text-teal-600">
                Symptoms
              </p>

            </div>

            <h3 className="mt-4 text-2xl font-bold text-slate-900">
              Tell us about your symptoms
            </h3>

            <p className="mt-2 text-slate-500">
              Search and select the symptoms you are experiencing.
            </p>

          </div>

          {/* Selected symptoms */}

          <div className="mb-7 min-h-16 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4">

            {selectedSymptoms.length > 0 ? (

              <div>

                <div className="mb-2 flex items-center justify-between">

                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Selected symptoms
                  </p>

                  <span className="rounded-full bg-teal-100 px-2.5 py-1 text-xs font-bold text-teal-700">
                    {selectedSymptoms.length}
                  </span>

                </div>

                <div className="flex flex-wrap gap-2">

                  {selectedSymptoms.map((symptom) => (

                    <button
                      key={symptom}
                      type="button"
                      onClick={() => toggleSymptom(symptom)}
                      disabled={loading}
                      className="max-w-full break-words rounded-full bg-teal-100 px-3 py-2 text-xs font-medium text-teal-800 transition hover:bg-teal-200 disabled:cursor-not-allowed disabled:opacity-60 sm:px-4 sm:text-sm"
                    >
                      {symptom} ×
                    </button>

                  ))}

                </div>

              </div>

            ) : (

              <div className="flex items-center gap-3">

                <span className="text-lg text-slate-400">
                  +
                </span>

                <p className="text-sm text-slate-400">
                  Selected symptoms will appear here.
                </p>

              </div>

            )}

          </div>

          {/* Search */}

          <div>

            <label
              htmlFor="symptom-search"
              className="mb-2 block text-sm font-semibold text-slate-700"
            >
              Search symptoms
            </label>

            <div className="relative">

              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-lg text-slate-400">
                🔎
              </span>

              <input
                id="symptom-search"
                type="text"
                value={searchTerm}
                onChange={(event) =>
                  setSearchTerm(event.target.value)
                }
                placeholder="Search symptoms, e.g. fever, headache, breathing..."
                disabled={loading || symptomsLoading}
                className="h-14 w-full rounded-xl border border-slate-200 bg-white pl-12 pr-16 text-sm outline-none transition placeholder:text-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              />

              {searchTerm && (

                <button
                  type="button"
                  onClick={() => setSearchTerm("")}
                  disabled={loading}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400 transition hover:text-slate-700"
                >
                  Clear
                </button>

              )}

            </div>

          </div>

          {/* Symptom list */}

          <div className="mt-5">

            {symptomsLoading ? (

              <div className="rounded-2xl border border-teal-100 bg-teal-50 p-5">

                <div className="flex items-center gap-3">

                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-teal-600 border-t-transparent" />

                  <p className="text-sm font-medium text-teal-800">
                    Loading available symptoms...
                  </p>

                </div>

              </div>

            ) : symptomsError ? (

              <div className="rounded-2xl border border-red-200 bg-red-50 p-5">

                <p className="text-sm font-semibold text-red-800">
                  Unable to load symptoms
                </p>

                <p className="mt-1 text-sm text-red-700">
                  {symptomsError}
                </p>

                <p className="mt-3 text-xs text-red-600">
                  You can still use the custom symptom field below.
                </p>

              </div>

            ) : (

              <div>

                <div className="mb-3 flex items-center justify-between">

                  <p className="text-sm font-semibold text-slate-700">

                    {searchTerm
                      ? "Matching symptoms"
                      : "Available symptoms"}

                  </p>

                  <span className="text-xs text-slate-400">

                    {filteredSymptoms.length}{" "}
                    {filteredSymptoms.length === 1
                      ? "symptom"
                      : "symptoms"}

                  </span>

                </div>

                {filteredSymptoms.length > 0 ? (

                  <div className="max-h-72 overflow-x-hidden overflow-y-auto rounded-2xl border border-slate-200 bg-slate-50 p-2 sm:p-3">

                    <div className="grid gap-2 sm:grid-cols-2">

                      {filteredSymptoms.map((symptom) => (

                        <button
                          key={symptom}
                          type="button"
                          onClick={() =>
                            toggleSymptom(symptom)
                          }
                          disabled={loading}
                          className="min-w-0 rounded-xl border border-slate-200 bg-white px-3 py-3 text-left text-sm font-medium text-slate-600 transition hover:border-teal-300 hover:bg-teal-50 hover:text-teal-700 disabled:cursor-not-allowed disabled:opacity-60 sm:px-4"
                        >

                          <span className="mr-2 text-teal-600">
                            +
                          </span>

                          {symptom}

                        </button>

                      ))}

                    </div>

                  </div>

                ) : (

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 text-center">

                    <div className="text-2xl">
                      🔍
                    </div>

                    <p className="mt-2 text-sm font-semibold text-slate-700">
                      No matching symptoms found
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Try another search term or add the symptom
                      manually below.
                    </p>

                  </div>

                )}

              </div>

            )}

          </div>

          {/* Custom symptom */}

          <div className="mt-8">

            <label
              htmlFor="custom-symptom"
              className="mb-2 block text-sm font-semibold text-slate-700"
            >
              Add another symptom manually
            </label>

            <div className="flex flex-col gap-3 sm:flex-row">

              <input
                id="custom-symptom"
                type="text"
                value={customSymptom}
                onChange={(event) =>
                  setCustomSymptom(event.target.value)
                }
                onKeyDown={handleCustomSymptomKeyDown}
                placeholder="Example: chest pain"
                disabled={loading}
                className="h-12 flex-1 rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              />

              <button
                type="button"
                onClick={addCustomSymptom}
                disabled={
                  loading || !customSymptom.trim()
                }
                className="h-12 rounded-xl border border-slate-200 px-6 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Add symptom
              </button>

            </div>

            <p className="mt-2 text-xs text-slate-400">
              You can also enter a symptom manually. The backend
              will determine whether it is recognized.
            </p>

          </div>

          {/* Analyze */}

          <div className="mt-10">

            <button
              type="button"
              onClick={analyzeSymptoms}
              disabled={
                selectedSymptoms.length === 0 ||
                loading
              }
              className="w-full rounded-xl bg-teal-700 px-6 py-4 text-base font-semibold text-white shadow-sm transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            >

              {loading ? (

                <span className="flex items-center justify-center gap-3">

                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />

                  Analyzing Symptoms...

                </span>

              ) : (

                "Analyze My Symptoms"

              )}

            </button>

          </div>

          {/* Loading */}

          {loading && (

            <div className="mt-6 overflow-hidden rounded-2xl border border-teal-100 bg-teal-50">

              <div className="h-1 w-full overflow-hidden bg-teal-100">

                <div className="h-full w-1/3 animate-pulse rounded-full bg-teal-600" />

              </div>

              <div className="p-6">

                <div className="flex items-start gap-4">

                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white shadow-sm">

                    <span className="h-6 w-6 animate-spin rounded-full border-2 border-teal-600 border-t-transparent" />

                  </div>

                  <div className="flex-1">

                    <h4 className="font-bold text-slate-900">
                      Analyzing your symptoms
                    </h4>

                    <p className="mt-1 text-sm leading-6 text-slate-600">
                      AI HealthMate is processing your selected
                      symptoms and generating the prediction.
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2">

                      <span className="rounded-full bg-white px-3 py-1.5 text-xs font-medium text-teal-700 ring-1 ring-teal-100">

                        {selectedSymptoms.length}{" "}
                        {selectedSymptoms.length === 1
                          ? "symptom"
                          : "symptoms"}{" "}
                        selected

                      </span>

                      <span className="rounded-full bg-white px-3 py-1.5 text-xs font-medium text-slate-600 ring-1 ring-slate-200">
                        🤖 AI model running
                      </span>

                    </div>

                  </div>

                </div>

              </div>

            </div>

          )}

          {/* Error */}

          {error && !loading && (

            <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-700">

              <strong>Error:</strong>{" "}

              {error}

            </div>

          )}

          {/* Safety */}

          <div className="mt-6 rounded-2xl bg-amber-50 p-4 text-sm leading-6 text-amber-800">

            <strong>Important:</strong> AI HealthMate is an
            educational decision-support system. Its predictions
            are not a medical diagnosis and should not replace
            professional medical advice.

          </div>

        </div>

      </section>

      {/* ================================================== */}
      {/* RESULTS */}
      {/* ================================================== */}

      {result && !loading && (

        <section
          id="results"
          className="scroll-mt-24 mx-auto max-w-5xl px-4 pb-12 sm:px-6 sm:pb-14"
        >

          <div className="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-slate-200">

            {/* Result header */}

            <div className="border-b border-slate-200 bg-gradient-to-r from-teal-50 to-white p-6 sm:p-10">

              <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

                <div>

                  <div className="flex items-center gap-3">

                    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-100 font-bold text-teal-700">
                      2
                    </span>

                    <p className="text-sm font-semibold uppercase tracking-wider text-teal-600">
                      Analysis complete
                    </p>

                  </div>

                  <h3 className="mt-4 break-words text-2xl font-bold text-slate-900 sm:text-3xl">
                    Your AI HealthMate Result
                  </h3>

                  <p className="mt-2 text-sm text-slate-500">
                    Based on the symptoms you provided.
                  </p>

                </div>

                <button
                  type="button"
                  onClick={startNewAnalysis}
                  className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-teal-300 hover:text-teal-700"
                >
                  + Check Another
                </button>

              </div>

            </div>

            <div className="p-6 sm:p-10">

              {/* Emergency */}

              {result.emergency_warning && (

                <div className="mb-10 overflow-hidden rounded-3xl border-2 border-red-300 bg-red-50 shadow-sm">

                  <div className="border-b border-red-200 bg-red-100 px-5 py-4 sm:px-6">

                    <div className="flex items-center gap-3">

                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-600 text-xl text-white shadow-sm">
                        ⚠️
                      </div>

                      <div>

                        <p className="text-xs font-bold uppercase tracking-wider text-red-700">
                          Urgent Safety Alert
                        </p>

                        <h4 className="mt-0.5 text-xl font-bold text-red-900">
                          Emergency symptoms detected
                        </h4>

                      </div>

                    </div>

                  </div>

                  <div className="p-5 sm:p-6">

                    <p className="text-sm font-semibold leading-6 text-red-900 sm:text-base">

                      {result.emergency_warning_message ||
                        "Some of the symptoms you entered may require urgent medical attention."}

                    </p>

                    {result.emergency_symptoms.length > 0 && (

                      <div className="mt-5">

                        <p className="text-xs font-bold uppercase tracking-wider text-red-700">
                          Detected emergency symptoms
                        </p>

                        <div className="mt-3 grid gap-2 sm:grid-cols-2">

                          {result.emergency_symptoms.map(
                            (symptom) => (

                              <div
                                key={symptom}
                                className="flex items-center gap-3 rounded-xl border border-red-200 bg-white px-4 py-3"
                              >

                                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-red-100 text-sm text-red-700">
                                  !
                                </span>

                                <span className="break-words text-sm font-semibold capitalize text-red-800">
                                  {symptom}
                                </span>

                              </div>

                            )
                          )}

                        </div>

                      </div>

                    )}

                    <div className="mt-6 rounded-2xl border border-red-200 bg-white p-5">

                      <div className="flex items-start gap-3">

                        <span className="text-xl">
                          🏥
                        </span>

                        <div>

                          <h5 className="font-bold text-red-900">
                            What you should do
                          </h5>

                          <p className="mt-2 text-sm leading-6 text-slate-700">

                            If you are experiencing severe,
                            sudden, or worsening symptoms, seek
                            immediate medical attention or contact
                            your local emergency service.

                          </p>

                        </div>

                      </div>

                    </div>

                    <div className="mt-4 rounded-2xl bg-red-100 p-4">

                      <p className="text-xs font-medium leading-5 text-red-800 sm:text-sm">

                        <strong>
                          Do not rely on this AI prediction during
                          an emergency.
                        </strong>{" "}
                        AI HealthMate is an educational
                        decision-support system and cannot assess
                        your condition in place of a healthcare
                        professional.

                      </p>

                    </div>

                  </div>

                </div>

              )}

              {/* Prediction */}

              <div className="rounded-3xl border border-teal-100 bg-teal-50 p-6 sm:p-8">

                <p className="text-sm font-semibold uppercase tracking-wider text-teal-700">
                  Possible condition
                </p>

                <h4 className="mt-3 break-words text-2xl font-bold capitalize text-slate-900 sm:text-4xl">
                  {result.predicted_disease}
                </h4>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
                  This is a model-generated prediction based on
                  the symptoms provided. It is not a medical
                  diagnosis.
                </p>

                <div className="mt-6 grid gap-4 sm:grid-cols-2">

                  <div className="rounded-2xl bg-white p-5 ring-1 ring-teal-100">

                    <div className="flex flex-wrap items-center justify-between gap-3">

                      <p className="text-sm font-medium text-slate-500">
                        Model score
                      </p>

                      <span className="text-lg font-bold text-teal-700">
                        {result.model_score.toFixed(2)}%
                      </span>

                    </div>

                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">

                      <div
                        className="h-full rounded-full bg-teal-600 transition-all"
                        style={{
                          width: `${Math.min(
                            result.model_score,
                            100
                          )}%`,
                        }}
                      />

                    </div>

                    <p className="mt-2 text-xs text-slate-400">
                      Model score, not clinical probability
                    </p>

                  </div>

                  <div className="rounded-2xl bg-white p-5 ring-1 ring-teal-100">

                    <div className="flex flex-wrap items-center justify-between gap-3">

                      <p className="text-sm font-medium text-slate-500">
                        Confidence level
                      </p>

                      <span
                        className={`rounded-full px-3 py-1 text-xs font-bold capitalize ${
                          getConfidenceStyle().badge
                        }`}
                      >
                        {result.confidence_level}
                      </span>

                    </div>

                    <div className="mt-4">

                      <div className="h-2 overflow-hidden rounded-full bg-slate-100">

                        <div
                          className={`h-full rounded-full ${
                            getConfidenceStyle().bar
                          }`}
                          style={{
                            width: `${Math.min(
                              result.model_score,
                              100
                            )}%`,
                          }}
                        />

                      </div>

                    </div>

                  </div>

                </div>

              </div>

              {/* Confidence warning */}

              {result.confidence_warning && (

                <div className="mt-5 rounded-2xl border border-orange-200 bg-orange-50 p-4 text-sm leading-6 text-orange-800">

                  <strong>Confidence notice:</strong>{" "}

                  {result.confidence_warning_message}

                </div>

              )}

              {/* Symptom warning */}

              {result.symptom_warning && (

                <div className="mt-5 rounded-2xl border border-yellow-200 bg-yellow-50 p-4 text-sm leading-6 text-yellow-800">

                  <strong>Symptom notice:</strong>{" "}

                  {result.symptom_warning_message}

                </div>

              )}

              {/* Recognized / Unrecognized */}

              <div className="mt-10 grid gap-5 md:grid-cols-2">

                <div className="rounded-2xl border border-slate-200 p-5">

                  <div className="flex flex-wrap items-center justify-between gap-3">

                    <h4 className="font-semibold text-slate-900">
                      Recognized symptoms
                    </h4>

                    <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                      {result.recognized_symptoms.length}
                    </span>

                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">

                    {result.recognized_symptoms.map(
                      (symptom) => (

                        <span
                          key={symptom}
                          className="rounded-full bg-green-50 px-3 py-1.5 text-sm text-green-700"
                        >
                          ✓ {symptom}
                        </span>

                      )
                    )}

                  </div>

                </div>

                <div className="rounded-2xl border border-slate-200 p-5">

                  <div className="flex flex-wrap items-center justify-between gap-3">

                    <h4 className="font-semibold text-slate-900">
                      Unrecognized symptoms
                    </h4>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                      {result.unrecognized_symptoms.length}
                    </span>

                  </div>

                  {result.unrecognized_symptoms.length > 0 ? (

                    <div className="mt-4 flex flex-wrap gap-2">

                      {result.unrecognized_symptoms.map(
                        (symptom) => (

                          <span
                            key={symptom}
                            className="rounded-full bg-red-50 px-3 py-1.5 text-sm text-red-700"
                          >
                            {symptom}
                          </span>

                        )
                      )}

                    </div>

                  ) : (

                    <p className="mt-4 text-sm text-slate-500">
                      All entered symptoms were recognized.
                    </p>

                  )}

                </div>

              </div>

              {/* Description */}

              <div className="mt-10 rounded-2xl border border-slate-200 p-6">

                <div className="flex items-center gap-3">

                  <span className="text-2xl">
                    📖
                  </span>

                  <h4 className="break-words text-xl font-bold text-slate-900">
                    About the condition
                  </h4>

                </div>

                <p className="mt-4 leading-7 text-slate-600">
                  {result.description}
                </p>

              </div>

              {/* Top predictions */}

              <div className="mt-10">

                <h4 className="break-words text-xl font-bold text-slate-900">
                  Top Predictions
                </h4>

                <p className="mt-1 text-sm text-slate-500">
                  Other conditions ranked by the model.
                </p>

                <div className="mt-5 space-y-4">

                  {result.top_predictions.map(
                    (prediction, index) => (

                      <div
                        key={prediction.disease}
                        className="rounded-2xl border border-slate-200 p-5"
                      >

                        <div className="flex flex-wrap items-center justify-between gap-3">

                          <div className="flex items-center gap-3">

                            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-600">
                              {index + 1}
                            </span>

                            <span className="min-w-0 break-words font-semibold capitalize text-slate-800">
                              {prediction.disease}
                            </span>

                          </div>

                          <span className="shrink-0 text-sm font-bold text-teal-700">
                            {prediction.model_score.toFixed(2)}%
                          </span>

                        </div>

                        <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">

                          <div
                            className="h-full rounded-full bg-teal-500"
                            style={{
                              width: `${Math.min(
                                prediction.model_score,
                                100
                              )}%`,
                            }}
                          />

                        </div>

                      </div>

                    )
                  )}

                </div>

              </div>

              {/* Recommendations */}

              <div className="mt-12">

                <h4 className="text-2xl font-bold text-slate-900">
                  Health Information & Recommendations
                </h4>

                <p className="mt-2 text-sm text-slate-500">
                  General educational information associated
                  with the predicted condition.
                </p>

                <div className="mt-6 grid gap-5 md:grid-cols-2">

                  {/* Medications */}

                  <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 transition hover:shadow-sm sm:p-6">

                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-xl">
                        💊
                      </div>

                      <h5 className="font-bold text-slate-900">
                        Medications
                      </h5>

                    </div>

                    <ul className="mt-5 space-y-3 text-sm text-slate-600">

                      {result.medications.map((item) => (

                        <li
                          key={item}
                          className="flex gap-2"
                        >

                          <span className="text-teal-600">
                            •
                          </span>

                          <span>
                            {item}
                          </span>

                        </li>

                      ))}

                    </ul>

                  </div>

                  {/* Precautions */}

                  <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 transition hover:shadow-sm sm:p-6">

                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50 text-xl">
                        🛡️
                      </div>

                      <h5 className="font-bold text-slate-900">
                        Precautions
                      </h5>

                    </div>

                    <ul className="mt-5 space-y-3 text-sm text-slate-600">

                      {result.precautions.map((item) => (

                        <li
                          key={item}
                          className="flex gap-2"
                        >

                          <span className="text-teal-600">
                            •
                          </span>

                          <span>
                            {item}
                          </span>

                        </li>

                      ))}

                    </ul>

                  </div>

                  {/* Diet */}

                  <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 transition hover:shadow-sm sm:p-6">

                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-50 text-xl">
                        🥗
                      </div>

                      <h5 className="font-bold text-slate-900">
                        Diet
                      </h5>

                    </div>

                    <ul className="mt-5 space-y-3 text-sm text-slate-600">

                      {result.diet.map((item) => (

                        <li
                          key={item}
                          className="flex gap-2"
                        >

                          <span className="text-teal-600">
                            •
                          </span>

                          <span>
                            {item}
                          </span>

                        </li>

                      ))}

                    </ul>

                  </div>

                  {/* Workout */}

                  <div className="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 transition hover:shadow-sm sm:p-6">

                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-xl">
                        🏃
                      </div>

                      <h5 className="font-bold text-slate-900">
                        Workout
                      </h5>

                    </div>

                    <ul className="mt-5 space-y-3 text-sm text-slate-600">

                      {result.workout.map((item) => (

                        <li
                          key={item}
                          className="flex gap-2"
                        >

                          <span className="text-teal-600">
                            •
                          </span>

                          <span>
                            {item}
                          </span>

                        </li>

                      ))}

                    </ul>

                  </div>

                </div>

              </div>

              {/* Disclaimer */}

              <div className="mt-10 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-800">

                <strong>Medical disclaimer:</strong> AI HealthMate
                provides educational information and model-generated
                predictions. The model score is not a clinical
                probability or medical diagnosis. Always consult a
                qualified healthcare professional for medical
                concerns.

              </div>

              {/* Bottom action */}

              <div className="mt-8 flex justify-center">

                <button
                  type="button"
                  onClick={startNewAnalysis}
                  className="rounded-xl bg-teal-700 px-7 py-3 text-sm font-semibold text-white transition hover:bg-teal-800"
                >
                  Check Another Symptoms
                </button>

              </div>

            </div>

          </div>

        </section>

      )}

      {/* ================================================== */}
      {/* HOW IT WORKS */}
      {/* ================================================== */}

      <section
        id="how-it-works"
        className="scroll-mt-24 border-t border-slate-200 bg-white"
      >

        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-16">

          <div className="text-center">

            <p className="text-sm font-semibold uppercase tracking-wider text-teal-600">
              How it works
            </p>

            <h3 className="mt-2 break-words text-2xl font-bold text-slate-900 sm:text-3xl">
              From symptoms to insights
            </h3>

            <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-500">
              AI HealthMate follows a structured pipeline to
              process symptoms and provide model-generated health
              information.
            </p>

          </div>

          <div className="mt-10 grid gap-5 md:grid-cols-3">

            <div className="rounded-2xl border border-slate-200 p-6 transition hover:-translate-y-1 hover:shadow-sm">

              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-2xl">
                📝
              </div>

              <h4 className="mt-5 font-semibold text-slate-900">
                1. Enter symptoms
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Search the available symptom list and select the
                symptoms you are experiencing.
              </p>

            </div>

            <div className="rounded-2xl border border-slate-200 p-6 transition hover:-translate-y-1 hover:shadow-sm">

              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-2xl">
                🤖
              </div>

              <h4 className="mt-5 font-semibold text-slate-900">
                2. AI analysis
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                The trained machine learning model analyzes the
                selected symptoms and generates possible
                predictions.
              </p>

            </div>

            <div className="rounded-2xl border border-slate-200 p-6 transition hover:-translate-y-1 hover:shadow-sm">

              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-2xl">
                💡
              </div>

              <h4 className="mt-5 font-semibold text-slate-900">
                3. Get insights
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                View the prediction, model score, alternative
                predictions, and available health information.
              </p>

            </div>

          </div>

        </div>

      </section>

      {/* ================================================== */}
      {/* ABOUT */}
      {/* ================================================== */}

      <section
        id="about"
        className="scroll-mt-24 border-t border-slate-200 bg-slate-50"
      >

        <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">

          <div className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-slate-200 sm:p-10">

            <div className="text-center">

              <p className="text-sm font-semibold uppercase tracking-wider text-teal-600">
                About AI HealthMate
              </p>

              <h3 className="mt-2 break-words text-2xl font-bold text-slate-900 sm:text-3xl">
                AI-powered health decision support
              </h3>

            </div>

            <div className="mt-8 grid gap-8 md:grid-cols-2">

              <div>

                <h4 className="text-lg font-bold text-slate-900">
                  What is AI HealthMate?
                </h4>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  AI HealthMate is an educational health
                  decision-support application that accepts
                  user-provided symptoms and uses a trained
                  machine learning model to generate possible
                  disease predictions.
                </p>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  The system also presents model scores,
                  alternative predictions, condition descriptions,
                  precautions, diet information, workout
                  information, and general medication information.
                </p>

              </div>

              <div>

                <h4 className="text-lg font-bold text-slate-900">
                  What does it provide?
                </h4>

                <div className="mt-4 space-y-3">

                  <div className="flex gap-3 rounded-xl bg-slate-50 p-4">

                    <span>
                      🤖
                    </span>

                    <div>

                      <p className="text-sm font-semibold text-slate-800">
                        AI prediction
                      </p>

                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        A model-generated possible condition based
                        on the selected symptoms.
                      </p>

                    </div>

                  </div>

                  <div className="flex gap-3 rounded-xl bg-slate-50 p-4">

                    <span>
                      📊
                    </span>

                    <div>

                      <p className="text-sm font-semibold text-slate-800">
                        Prediction insights
                      </p>

                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        Model score, confidence information, and
                        alternative predictions.
                      </p>

                    </div>

                  </div>

                  <div className="flex gap-3 rounded-xl bg-slate-50 p-4">

                    <span>
                      💡
                    </span>

                    <div>

                      <p className="text-sm font-semibold text-slate-800">
                        Health information
                      </p>

                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        General educational recommendations related
                        to the predicted condition.
                      </p>

                    </div>

                  </div>

                </div>

              </div>

            </div>

            <div className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 p-5">

              <p className="text-sm leading-6 text-amber-800">

                <strong>Important:</strong> AI HealthMate is not a
                substitute for professional medical care. Model
                scores are not clinical probabilities, and
                predictions should not be treated as medical
                diagnoses.

              </p>

            </div>

          </div>

        </div>

      </section>

      {/* ================================================== */}
      {/* FOOTER */}
      {/* ================================================== */}

      <footer className="border-t border-slate-200 bg-white">

        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-8 text-center sm:px-6 sm:flex-row sm:text-left">

          <div>

            <p className="font-semibold text-slate-700">
              AI HealthMate
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Educational AI-powered health decision-support system.
            </p>

          </div>

          <button
            type="button"
            onClick={() => scrollToSection("home")}
            className="rounded-lg px-4 py-2 text-sm font-semibold text-teal-700 transition hover:bg-teal-50"
          >
            Back to top ↑
          </button>

        </div>

      </footer>

    </main>
  );
}