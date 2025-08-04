import React, { useState, useCallback, useMemo } from 'react';
import { ChevronDown, Search, Type, Star, Upload } from 'lucide-react';
import { FontSelectorProps, FontInfo } from '../types';

const FontSelector: React.FC<FontSelectorProps> = ({
  fonts,
  selectedFont,
  onFontChange,
  previewText = 'Sample Text',
  showPreview = true,
  disabled = false,
  placeholder = 'Select a font...'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [favorites, setFavorites] = useState<string[]>([]);

  // Filter and sort fonts
  const filteredFonts = useMemo(() => {
    let filtered = fonts;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(font => 
        font.family.toLowerCase().includes(query) ||
        font.variants?.some(variant => variant.toLowerCase().includes(query))
      );
    }

    // Sort: favorites first, then web-safe, then uploaded, then alphabetically
    return filtered.sort((a, b) => {
      // Favorites first
      const aFav = favorites.includes(a.id);
      const bFav = favorites.includes(b.id);
      if (aFav && !bFav) return -1;
      if (!aFav && bFav) return 1;

      // Then by type (web-safe first)
      if (a.type !== b.type) {
        if (a.type === 'web-safe') return -1;
        if (b.type === 'web-safe') return 1;
      }

      // Finally alphabetically
      return a.family.localeCompare(b.family);
    });
  }, [fonts, searchQuery, favorites]);

  const handleFontSelect = useCallback((font: FontInfo) => {
    onFontChange(font);
    setIsOpen(false);
  }, [onFontChange]);

  const toggleFavorite = useCallback((fontId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setFavorites(prev => 
      prev.includes(fontId)
        ? prev.filter(id => id !== fontId)
        : [...prev, fontId]
    );
  }, []);

  const renderFontButton = () => {
    const displayFont = selectedFont || { family: placeholder, type: 'placeholder' as const };
    
    return (
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full flex items-center justify-between px-3 py-2 border rounded-lg transition-all ${
          disabled
            ? 'bg-gray-100 border-gray-300 cursor-not-allowed opacity-50'
            : isOpen
            ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-20'
            : 'border-gray-300 hover:border-gray-400 bg-white'
        }`}
      >
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <Type size={16} className="text-gray-600 flex-shrink-0" />
          <div className="text-left min-w-0 flex-1">
            <div 
              className={`font-medium truncate ${
                selectedFont ? 'text-gray-900' : 'text-gray-500'
              }`}
              style={selectedFont ? { fontFamily: selectedFont.family } : {}}
            >
              {displayFont.family}
            </div>
            {selectedFont && (
              <div className="text-xs text-gray-500 truncate">
                {selectedFont.type === 'uploaded' ? (
                  <span className="flex items-center space-x-1">
                    <Upload size={12} />
                    <span>Custom</span>
                  </span>
                ) : (
                  'Web Safe'
                )}
                {selectedFont.variants && (
                  <span className="ml-2">
                    {selectedFont.variants.slice(0, 2).join(', ')}
                    {selectedFont.variants.length > 2 && '...'}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        <ChevronDown 
          size={16} 
          className={`text-gray-400 transition-transform ${
            isOpen ? 'transform rotate-180' : ''
          }`} 
        />
      </button>
    );
  };

  const renderSearchBar = () => (
    <div className="p-3 border-b border-gray-200">
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search fonts..."
          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          autoFocus
        />
      </div>
    </div>
  );

  const renderFontList = () => {
    if (filteredFonts.length === 0) {
      return (
        <div className="p-4 text-center text-gray-500">
          <Type size={24} className="mx-auto mb-2 opacity-50" />
          <p className="text-sm">
            {searchQuery ? 'No fonts found matching your search' : 'No fonts available'}
          </p>
        </div>
      );
    }

    return (
      <div className="max-h-64 overflow-y-auto">
        {filteredFonts.map((font) => {
          const isFavorite = favorites.includes(font.id);
          const isSelected = selectedFont?.id === font.id;
          
          return (
            <div
              key={font.id}
              onClick={() => handleFontSelect(font)}
              className={`px-3 py-3 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0 ${
                isSelected
                  ? 'bg-blue-50 text-blue-900'
                  : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <div 
                      className={`font-medium truncate ${
                        isSelected ? 'text-blue-900' : 'text-gray-900'
                      }`}
                      style={{ fontFamily: font.family }}
                    >
                      {font.family}
                    </div>
                    
                    {font.type === 'uploaded' && (
                      <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                        Custom
                      </span>
                    )}
                    
                    {isFavorite && (
                      <Star size={12} className="text-yellow-500 fill-current flex-shrink-0" />
                    )}
                  </div>
                  
                  <div className={`text-xs mt-1 ${
                    isSelected ? 'text-blue-700' : 'text-gray-500'
                  }`}>
                    {font.variants?.join(', ') || 'Regular'}
                  </div>
                  
                  {showPreview && (
                    <div 
                      className={`text-sm mt-2 truncate ${
                        isSelected ? 'text-blue-800' : 'text-gray-700'
                      }`}
                      style={{ fontFamily: font.family }}
                    >
                      {previewText}
                    </div>
                  )}
                </div>
                
                <button
                  onClick={(e) => toggleFavorite(font.id, e)}
                  className={`p-1 rounded transition-colors ${
                    isFavorite
                      ? 'text-yellow-500 hover:text-yellow-600'
                      : 'text-gray-400 hover:text-yellow-500'
                  }`}
                  title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                  <Star size={14} className={isFavorite ? 'fill-current' : ''} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderDropdown = () => {
    if (!isOpen) return null;

    return (
      <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
        {renderSearchBar()}
        {renderFontList()}
        
        {/* Footer */}
        <div className="p-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-600">
          <div className="flex items-center justify-between">
            <span>{filteredFonts.length} fonts available</span>
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1">
                <Star size={12} className="text-yellow-500" />
                <span>{favorites.length} favorites</span>
              </span>
              <span className="flex items-center space-x-1">
                <Upload size={12} className="text-purple-500" />
                <span>{fonts.filter(f => f.type === 'uploaded').length} custom</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="relative">
      {renderFontButton()}
      {renderDropdown()}
      
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default FontSelector;