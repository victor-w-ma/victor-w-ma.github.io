module Jekyll
  module CharacterCount
    def character_count(input)
      input.strip.length
    end
  end
end

Liquid::Template.register_filter(Jekyll::CharacterCount)
